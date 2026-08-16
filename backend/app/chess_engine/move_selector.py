"""
Glue: gets MultiPV candidates from Stockfish, re-ranks them against the
player's active WeaknessRecords via patch_engine, plays the top result.
This is what makes adaptation actually observable in play.

Below HANDOFF_ELO, Stockfish's own strength options can't produce
authentic weak play (see weak_play.py), so move selection routes through
the softmax sampler instead and skips patch_engine entirely - there's no
adaptation memory to defend yet at a player's first games, and layering
re-ranking on top of intentionally-noisy play would just muddy both
signals.
"""
from __future__ import annotations

import chess

from app.adaptation.patch_engine import rerank_candidates
from app.chess_engine.engine_wrapper import EngineWrapper
from app.chess_engine.weak_play import HANDOFF_ELO, weak_move
from app.models.db_models import WeaknessRecord

WEAK_PLAY_DEPTH = 3  # shallow on purpose - see weak_play.py


def _search_budget(target_elo: int) -> tuple[int, int]:
    """(depth, multipv). Stronger opposition -> deeper search over fewer
    candidates; weaker -> shallower and wider so real blunders surface."""
    if target_elo < 1600:
        return 6, 14
    if target_elo < 2000:
        return 9, 10
    if target_elo < 2400:
        return 11, 6
    return 13, 5


def select_move(
    engine: EngineWrapper,
    board: chess.Board,
    records: list[WeaknessRecord],
    target_elo: int = 1000,
) -> chess.Move:
    if target_elo < HANDOFF_ELO:
        return weak_move(engine, board, target_elo=target_elo, depth=WEAK_PLAY_DEPTH)

    engine.configure_elo(max(HANDOFF_ELO, target_elo))
    depth, multipv = _search_budget(target_elo)
    candidates = engine.multipv_candidates(board, depth=depth, n=multipv)
    if not candidates:
        return engine.best_move(board, depth=depth)

    if records:
        candidates = rerank_candidates(engine, board, candidates, records, board.turn)

    return candidates[0][0]