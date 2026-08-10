from __future__ import annotations

import chess

from app.adaptation.signature_extractor import Signature, _development, _king_safety, _phase
from app.adaptation.similarity import similarity
from app.models.db_models import WeaknessRecord


def projected_signature(board: chess.Board, move: chess.Move, player_color: chess.Color) -> Signature:
    next_board = board.copy(stack=False)
    next_board.push(move)
    return Signature("projected", [], _phase(next_board), {
        "king_safety": _king_safety(next_board, player_color),
        "development": _development(next_board, player_color),
        "attack_pressure": 0.0, "material_swing": 0.0,
    })


def rerank(board: chess.Board, candidates: list[tuple[chess.Move, float]], records: list[WeaknessRecord], player_color: chess.Color) -> list[tuple[chess.Move, float]]:
    adjusted = []
    for move, white_score in candidates:
        projection = projected_signature(board, move, player_color)
        penalty = 0.0
        for record in records:
            representative = Signature(record.phenomenon, record.motifs, record.phase, record.representative_features)
            if (similarity(projection, representative) or 0) >= 0.75:
                penalty += (0.2 if record.status == "watching" else 1.5) * record.confidence * 100
        # Stockfish evaluations use White's POV. Mahoraga plays Black in v1,
        # so a larger penalty means a less desirable candidate (higher White score).
        adjusted.append((move, white_score + penalty))
    return sorted(adjusted, key=lambda item: item[1])
