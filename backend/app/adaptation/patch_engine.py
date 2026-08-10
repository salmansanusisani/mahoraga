from __future__ import annotations

import chess

from app.adaptation.signature_extractor import (
    Signature,
    _detect_back_rank,
    _detect_king_attack,
    _detect_pin,
    _detect_sacrifice,
    _development,
    _is_forked,
    _king_safety,
    _phase,
)
from app.adaptation.similarity import similarity
from app.models.db_models import WeaknessRecord

# Mahoraga always plays Black in v1, so its learned weaknesses describe
# positions where Black loses. Projections must therefore describe BLACK's
# position, or they will never match the stored records.
LOSER_COLOR = chess.BLACK


def projected_signature(board: chess.Board, move: chess.Move, loser_color: chess.Color = LOSER_COLOR) -> Signature:
    next_board = board.copy(stack=False)
    next_board.push(move)
    mover_color = board.turn
    motifs = []
    if _is_forked(next_board, loser_color):
        motifs.append("fork")
    if _detect_pin(next_board, loser_color):
        motifs.append("pin")
    if _detect_king_attack(next_board, loser_color):
        motifs.append("king_attack")
    if _detect_back_rank(next_board, loser_color):
        motifs.append("back_rank")
    if _detect_sacrifice(board, move, mover_color):
        motifs.append("sacrifice")
    return Signature("projected", motifs, _phase(next_board), {
        "king_safety": _king_safety(next_board, loser_color),
        "development": _development(next_board, loser_color),
        "attack_pressure": 0.0, "material_swing": 0.0,
    })


def rerank(board: chess.Board, candidates: list[tuple[chess.Move, float]], records: list[WeaknessRecord], loser_color: chess.Color = LOSER_COLOR) -> list[tuple[chess.Move, float]]:
    adjusted = []
    for move, white_score in candidates:
        projection = projected_signature(board, move, loser_color)
        penalty = 0.0
        for record in records:
            representative = Signature(record.phenomenon, record.motifs, record.phase, record.representative_features)
            if (similarity(projection, representative) or 0) >= 0.75:
                penalty += (0.2 if record.status == "watching" else 1.5) * record.confidence * 100
        # Stockfish evaluations use White's POV. Mahoraga plays Black in v1,
        # so a larger penalty means a less desirable candidate (higher White score).
        adjusted.append((move, white_score + penalty))
    return sorted(adjusted, key=lambda item: item[1])
