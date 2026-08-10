from __future__ import annotations

import chess

from app.adaptation.patch_engine import rerank
from app.chess_engine.engine_wrapper import EngineWrapper
from app.models.db_models import WeaknessRecord


def select_move(engine: EngineWrapper, board: chess.Board, records: list[WeaknessRecord], skill_level: int = 5) -> chess.Move:
    engine.configure_strength(skill_level)
    candidates = engine.multipv_candidates(board, depth=8 if skill_level < 10 else 12, n=5)
    if not candidates:
        return engine.best_move(board)
    return rerank(board, candidates, records, chess.WHITE)[0][0]
