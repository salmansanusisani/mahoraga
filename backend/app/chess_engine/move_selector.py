from __future__ import annotations

import math
import random

import chess

from app.adaptation.patch_engine import rerank
from app.chess_engine.engine_wrapper import EngineWrapper
from app.models.db_models import WeaknessRecord


def _pick_with_skill(candidates: list[tuple[chess.Move, float]], skill_level: int) -> chess.Move:
    """
    Mimic Stockfish's Skill Level by choosing probabilistically among the
    re-ranked candidates. Temperature rises as skill drops, so a low-skill
    bot increasingly picks sub-optimal (blundering) moves; near skill 20 it
    effectively always plays the best move.
    """
    if skill_level >= 20 or len(candidates) <= 1:
        return candidates[0][0]
    best = candidates[0][1]
    temp_cp = 60 + (20 - skill_level) * 18
    weights = [math.exp(-max(0.0, score - best) / temp_cp) for _, score in candidates]
    total = sum(weights)
    draw = random.random() * total
    acc = 0.0
    for (move, _), weight in zip(candidates, weights):
        acc += weight
        if draw <= acc:
            return move
    return candidates[0][0]


def select_move(engine: EngineWrapper, board: chess.Board, records: list[WeaknessRecord], skill_level: int = 5) -> chess.Move:
    engine.configure_strength(skill_level)
    # Low skill: shallow search over a wide pool so real blunders surface.
    # High skill: deep search over the top candidates.
    if skill_level >= 14:
        depth, n = 12, 5
    elif skill_level >= 8:
        depth, n = 10, 8
    elif skill_level >= 4:
        depth, n = 8, 14
    else:
        depth, n = 5, 24
    candidates = engine.multipv_candidates(board, depth=depth, n=n)
    if not candidates:
        return engine.best_move(board)
    # rerank projects BLACK's (Mahoraga's) position by default to match the
    # records, which describe the loser (Black) of each learned game.
    reranked = rerank(board, candidates, records)
    return _pick_with_skill(reranked, skill_level)
