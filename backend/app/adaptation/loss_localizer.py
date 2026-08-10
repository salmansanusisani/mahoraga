"""
Given a full game (as a list of SAN/UCI moves or a python-chess Game),
find the ply where the losing side's position collapsed - the single
biggest eval swing against them.
"""
from __future__ import annotations

from dataclasses import dataclass

import chess
import chess.pgn

from app.chess_engine.engine_wrapper import EngineWrapper


@dataclass
class LossPoint:
    ply: int                  # index into the move list, 0-based
    board_before: chess.Board  # position before the losing move
    move: chess.Move           # the move that was played
    eval_before: float         # centipawns, White's perspective
    eval_after: float
    swing_against_loser: float  # positive = this ply is where it went wrong
    loser_color: chess.Color


def localize_loss(game: chess.pgn.Game, engine: EngineWrapper, depth: int = 12) -> LossPoint | None:
    """
    Walks the game, evaluating every position, and returns the ply with
    the largest eval swing against whoever eventually lost. Returns None
    if the game has no clear loser (e.g. a draw) or is too short to analyze.
    """
    result = game.headers.get("Result", "*")
    if result == "1-0":
        loser_color = chess.BLACK
    elif result == "0-1":
        loser_color = chess.WHITE
    else:
        return None  # draws / unknown results aren't in scope for loss signatures

    board = game.board()
    node = game
    prev_eval = engine.evaluate_cp(board, depth=depth)

    best: LossPoint | None = None
    ply = 0

    while node.variations:
        node = node.variations[0]
        move = node.move
        board_before = board.copy()
        board.push(move)
        cur_eval = engine.evaluate_cp(board, depth=depth)

        # swing from the loser's perspective: how much worse did their
        # position get on this move, regardless of who was to move
        if loser_color == chess.WHITE:
            swing = prev_eval - cur_eval
        else:
            swing = cur_eval - prev_eval

        if best is None or swing > best.swing_against_loser:
            best = LossPoint(
                ply=ply,
                board_before=board_before,
                move=move,
                eval_before=prev_eval,
                eval_after=cur_eval,
                swing_against_loser=swing,
                loser_color=loser_color,
            )

        prev_eval = cur_eval
        ply += 1

    return best
