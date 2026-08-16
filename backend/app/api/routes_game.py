from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import chess
import chess.pgn
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.adaptation.loss_localizer import localize_loss
from app.adaptation.signature_extractor import extract_signature
from app.adaptation.weakness_memory import active_records, decay_unseen, refresh_effectiveness, update_from_signature
from app.chess_engine.engine_wrapper import EngineWrapper
from app.chess_engine.move_selector import select_move
from app.chess_engine.weak_play import skill_to_elo
from app.db import get_session
from app.models.db_models import Game, Player
from app.models.schemas import GameCreate, GameResponse, MoveRequest
from app.profiling.player_profile import apply_opening_strength_signal, update_profile

router = APIRouter(prefix="/games", tags=["games"])


def _shared_engine(request: Request) -> EngineWrapper:
    """Reuse the app-lifetime Stockfish (started in main.startup). If it
    failed to start, fall back to a fresh per-request engine."""
    engine = getattr(request.app.state, "engine", None)
    if engine is not None:
        return engine
    return EngineWrapper()


def _game_or_404(session: Session, game_id: UUID) -> Game:
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(404, "Game not found")
    return game


def _board(game: Game) -> chess.Board:
    board = chess.Board()
    for uci in game.moves:
        board.push_uci(uci)
    return board


def _pgn(game: Game) -> chess.pgn.Game:
    pgn = chess.pgn.Game()
    pgn.headers.update({"Event": "Mahoraga", "White": "Player", "Black": "Mahoraga", "Result": game.result})
    node = pgn
    board = chess.Board()
    for uci in game.moves:
        move = chess.Move.from_uci(uci)
        node = node.add_variation(move)
        board.push(move)
    return pgn


def _finish(session: Session, game: Game, board: chess.Board, engine: EngineWrapper) -> str | None:
    game.result = board.result(claim_draw=True)
    game.ended_at = datetime.now(timezone.utc)
    game.pgn = str(_pgn(game))
    player = session.get(Player, game.player_id)
    if player is None:
        return None
    player.games_played += 1
    update_profile(player, game)
    if game.skill_level is None:
        if game.result == "1-0":
            player.estimated_strength = min(2400, player.estimated_strength + 100)
        elif game.result == "0-1":
            player.estimated_strength = max(50, player.estimated_strength - 100)
        else:
            player.estimated_strength = min(2400, player.estimated_strength + 50)
    if game.result == "1-0":
        player.player_wins += 1
        point = localize_loss(_pgn(game), engine, depth=10)
        if point:
            record = update_from_signature(session, player.id, game.id, extract_signature(point))
            decay_unseen(session, player.id, {record.id})
            refresh_effectiveness(session, player.id, player.games_played)
            return f"Mahoraga learned: {record.phenomenon.replace('_', ' ')} ({record.status})."
    elif game.result == "0-1":
        player.mahoraga_wins += 1
    else:
        player.draws += 1
    decay_unseen(session, player.id, set())
    refresh_effectiveness(session, player.id, player.games_played)
    return None


@router.post("", response_model=GameResponse)
def start_game(payload: GameCreate, request: Request, session: Session = Depends(get_session)):
    if not session.get(Player, payload.player_id):
        raise HTTPException(404, "Player not found")
    if payload.human_color not in ("white", "black"):
        raise HTTPException(422, "human_color must be 'white' or 'black'")
    player = session.get(Player, payload.player_id)
    game = Game(player_id=payload.player_id, fen=chess.STARTING_FEN, skill_level=payload.skill_level, human_color=payload.human_color)
    session.add(game)
    session.commit()
    session.refresh(game)

    first_move = None
    board = chess.Board()
    if payload.human_color == "black":
        # Mahoraga (White) opens the battle; the human answers as Black.
        try:
            engine = _shared_engine(request)
            if game.skill_level is not None:
                target_elo = skill_to_elo(game.skill_level)
            else:
                target_elo = player.estimated_strength
            first_move = select_move(engine, board, active_records(session, player.id), target_elo=target_elo).uci()
            board.push_uci(first_move)
            game.moves = [first_move]
            game.fen = board.fen()
            session.add(game)
            session.commit()
        except FileNotFoundError as error:
            raise HTTPException(
                503,
                "Stockfish is not configured. Set STOCKFISH_PATH to the full path of stockfish.exe, then restart Uvicorn.",
            ) from error

    return GameResponse(game_id=game.id, fen=game.fen, moves=game.moves, result="*", mahoraga_move=first_move, human_color=game.human_color)


@router.get("/{game_id}", response_model=GameResponse)
def get_game(game_id: UUID, session: Session = Depends(get_session)):
    game = _game_or_404(session, game_id)
    return GameResponse(game_id=game.id, fen=game.fen, moves=game.moves, result=game.result)


@router.get("/{game_id}/legal-moves")
def legal_moves(game_id: UUID, session: Session = Depends(get_session)):
    game = _game_or_404(session, game_id)
    board = _board(game)
    return {
        "moves": [
            {
                "uci": move.uci(),
                "to": chess.square_name(move.to_square),
                "capture": board.is_capture(move),
            }
            for move in board.legal_moves
        ]
    }


@router.post("/{game_id}/move", response_model=GameResponse)
def play_move(game_id: UUID, payload: MoveRequest, request: Request, session: Session = Depends(get_session)):
    game = _game_or_404(session, game_id)
    if game.result != "*":
        raise HTTPException(409, "This game has already ended")
    board = _board(game)
    try:
        move = chess.Move.from_uci(payload.move)
    except ValueError as error:
        raise HTTPException(400, "Send a legal UCI move, such as e2e4") from error
    if move not in board.legal_moves:
        raise HTTPException(400, "Illegal move")
    board_before = board.copy(stack=False)
    board.push(move)
    game.moves = [*game.moves, move.uci()]
    reply = None
    message = None
    if board.is_game_over(claim_draw=True):
        message = _finish(session, game, board, _shared_engine(request))
    else:
        player = session.get(Player, game.player_id)
        try:
            engine = _shared_engine(request)
            if game.skill_level is not None:
                target_elo = skill_to_elo(game.skill_level)
            else:
                if len(game.moves) <= 8:
                    expected = engine.evaluate_cp(board_before, depth=8)
                    actual = engine.evaluate_cp(board, depth=8)
                    apply_opening_strength_signal(player, max(0.0, expected - actual))
                target_elo = player.estimated_strength
            reply = select_move(engine, board, active_records(session, player.id), target_elo=target_elo)
        except FileNotFoundError as error:
            raise HTTPException(
                503,
                "Stockfish is not configured. Set STOCKFISH_PATH to the full path of stockfish.exe, then restart Uvicorn.",
            ) from error
        board.push(reply)
        game.moves = [*game.moves, reply.uci()]
        if board.is_game_over(claim_draw=True):
            message = _finish(session, game, board, engine)
    game.fen = board.fen()
    session.add(game)
    session.commit()
    return GameResponse(game_id=game.id, fen=game.fen, moves=game.moves, result=game.result, mahoraga_move=reply.uci() if reply else None, message=message)
