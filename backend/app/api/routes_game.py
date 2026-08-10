from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import chess
import chess.pgn
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.adaptation.loss_localizer import localize_loss
from app.adaptation.signature_extractor import extract_signature
from app.adaptation.weakness_memory import active_records, decay_unseen, refresh_effectiveness, update_from_signature
from app.chess_engine.engine_wrapper import EngineWrapper
from app.chess_engine.move_selector import select_move
from app.db import get_session
from app.models.db_models import Game, Player
from app.models.schemas import GameCreate, GameResponse, MoveRequest
from app.profiling.player_profile import apply_opening_strength_signal, update_profile

router = APIRouter(prefix="/games", tags=["games"])


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


def _finish(session: Session, game: Game, board: chess.Board) -> str | None:
    game.result = board.result(claim_draw=True)
    game.ended_at = datetime.now(timezone.utc)
    game.pgn = str(_pgn(game))
    player = session.get(Player, game.player_id)
    if player is None:
        return None
    player.games_played += 1
    update_profile(player, game)
    if game.result == "1-0":
        player.player_wins += 1
        with EngineWrapper() as engine:
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
def start_game(payload: GameCreate, session: Session = Depends(get_session)):
    if not session.get(Player, payload.player_id):
        raise HTTPException(404, "Player not found")
    game = Game(player_id=payload.player_id, fen=chess.STARTING_FEN)
    session.add(game)
    session.commit()
    session.refresh(game)
    return GameResponse(game_id=game.id, fen=game.fen, moves=[], result="*")


@router.get("/{game_id}", response_model=GameResponse)
def get_game(game_id: UUID, session: Session = Depends(get_session)):
    game = _game_or_404(session, game_id)
    return GameResponse(game_id=game.id, fen=game.fen, moves=game.moves, result=game.result)


@router.post("/{game_id}/move", response_model=GameResponse)
def play_move(game_id: UUID, payload: MoveRequest, session: Session = Depends(get_session)):
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
        message = _finish(session, game, board)
    else:
        player = session.get(Player, game.player_id)
        try:
            with EngineWrapper() as engine:
                if len(game.moves) <= 8:
                    expected = engine.evaluate_cp(board_before, depth=8)
                    actual = engine.evaluate_cp(board, depth=8)
                    apply_opening_strength_signal(player, max(0.0, expected - actual))
                reply = select_move(engine, board, active_records(session, player.id), skill_level=min(12, max(0, player.estimated_strength // 200)))
        except FileNotFoundError as error:
            raise HTTPException(
                503,
                "Stockfish is not configured. Set STOCKFISH_PATH to the full path of stockfish.exe, then restart Uvicorn.",
            ) from error
        board.push(reply)
        game.moves = [*game.moves, reply.uci()]
        if board.is_game_over(claim_draw=True):
            message = _finish(session, game, board)
    game.fen = board.fen()
    session.add(game)
    session.commit()
    return GameResponse(game_id=game.id, fen=game.fen, moves=game.moves, result=game.result, mahoraga_move=reply.uci() if reply else None, message=message)
