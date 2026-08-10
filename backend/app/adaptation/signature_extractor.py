"""
Turns a LossPoint into a Signature: motif tags + continuous features.
This is the core of the whole project - two differently-played losses
that share an underlying shape should produce similar signatures.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import chess

from app.adaptation.loss_localizer import LossPoint

MOTIF_VOCAB = [
    "fork",
    "pin",
    "king_attack",
    "back_rank",
    "sacrifice",
]

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}

START_MINOR_QUEEN_SQUARES = {
    chess.WHITE: [chess.B1, chess.G1, chess.C1, chess.F1, chess.D1],
    chess.BLACK: [chess.B8, chess.G8, chess.C8, chess.F8, chess.D8],
}


@dataclass
class Signature:
    phenomenon: str
    motifs: list[str]
    phase: str
    features: dict[str, float] = field(default_factory=dict)
    severity: float = 0.0
    ply: int = 0

    def to_dict(self) -> dict:
        return {
            "phenomenon": self.phenomenon,
            "motifs": self.motifs,
            "phase": self.phase,
            "features": self.features,
            "severity": self.severity,
            "ply": self.ply,
        }


def _piece_value(piece: chess.Piece | None) -> int:
    return PIECE_VALUES[piece.piece_type] if piece else 0


def _king_safety(board: chess.Board, color: chess.Color) -> float:
    king_sq = board.king(color)
    if king_sq is None:
        return 0.0
    adjacent = chess.SquareSet(chess.BB_KING_ATTACKS[king_sq])
    if not adjacent:
        return 0.0
    defenders = sum(1 for sq in adjacent if (p := board.piece_at(sq)) and p.color == color)
    score = defenders / len(adjacent)
    castled_squares = {chess.G1, chess.C1} if color == chess.WHITE else {chess.G8, chess.C8}
    if king_sq not in castled_squares:
        score *= 0.75
    return round(score, 3)


def _development(board: chess.Board, color: chess.Color) -> float:
    start_squares = START_MINOR_QUEEN_SQUARES[color]
    moved = sum(1 for sq in start_squares if board.piece_at(sq) is None)
    return round(moved / len(start_squares), 3)


def _detect_fork(board_after: chess.Board, move: chess.Move, mover_color: chess.Color) -> bool:
    piece = board_after.piece_at(move.to_square)
    if piece is None:
        return False
    targets = 0
    for sq in board_after.attacks(move.to_square):
        p = board_after.piece_at(sq)
        if p and p.color != mover_color and PIECE_VALUES[p.piece_type] >= 3:
            targets += 1
    return targets >= 2


def _is_forked(board: chess.Board, victim_color: chess.Color) -> bool:
    """True when any enemy piece currently attacks two or more of the
    victim's valuable pieces (>= a knight) at once."""
    attacker_color = not victim_color
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece and piece.color == attacker_color:
            targets = sum(
                1
                for target in board.attacks(sq)
                if (t := board.piece_at(target)) and t.color == victim_color and PIECE_VALUES[t.piece_type] >= 3
            )
            if targets >= 2:
                return True
    return False


def _detect_pin(board_after: chess.Board, target_color: chess.Color) -> bool:
    for sq in chess.SQUARES:
        p = board_after.piece_at(sq)
        if p and p.color == target_color and p.piece_type != chess.KING:
            if board_after.is_pinned(target_color, sq):
                return True
    return False


def _detect_king_attack(board_after: chess.Board, target_color: chess.Color) -> bool:
    king_sq = board_after.king(target_color)
    if king_sq is None:
        return False
    direct = len(board_after.attackers(not target_color, king_sq))
    adjacent_pressure = sum(
        len(board_after.attackers(not target_color, sq))
        for sq in chess.SquareSet(chess.BB_KING_ATTACKS[king_sq])
    )
    return direct > 0 or adjacent_pressure >= 2


def _detect_back_rank(board_after: chess.Board, target_color: chess.Color) -> bool:
    king_sq = board_after.king(target_color)
    if king_sq is None:
        return False
    home_rank = 0 if target_color == chess.WHITE else 7
    if chess.square_rank(king_sq) != home_rank:
        return False
    escapes = 0
    for sq in chess.SquareSet(chess.BB_KING_ATTACKS[king_sq]):
        if chess.square_rank(sq) != home_rank:
            occ = board_after.piece_at(sq)
            if occ is None or occ.color != target_color:
                escapes += 1
    return escapes == 0


def _detect_sacrifice(board_before: chess.Board, move: chess.Move, mover_color: chess.Color) -> bool:
    moving_piece = board_before.piece_at(move.from_square)
    if moving_piece is None:
        return False
    captured = board_before.piece_at(move.to_square)
    moved_value = PIECE_VALUES[moving_piece.piece_type]
    captured_value = _piece_value(captured)
    board_after = board_before.copy()
    board_after.push(move)
    defenders = board_after.attackers(not mover_color, move.to_square)
    return len(defenders) > 0 and moved_value > captured_value


def _phase(board: chess.Board) -> str:
    if board.fullmove_number <= 10:
        return "opening"
    major_minor_count = sum(
        1
        for sq in chess.SQUARES
        if (p := board.piece_at(sq)) and p.piece_type not in (chess.PAWN, chess.KING)
    )
    return "endgame" if major_minor_count <= 6 else "middlegame"


def extract_signature(loss_point: LossPoint) -> Signature:
    board_before = loss_point.board_before
    move = loss_point.move
    mover_color = board_before.turn  # side that played the losing move
    loser_color = loss_point.loser_color

    board_after = board_before.copy()
    board_after.push(move)

    motifs = []
    if _detect_fork(board_after, move, mover_color):
        motifs.append("fork")
    if _detect_pin(board_after, loser_color):
        motifs.append("pin")
    if _detect_king_attack(board_after, loser_color):
        motifs.append("king_attack")
    if _detect_back_rank(board_after, loser_color):
        motifs.append("back_rank")
    if _detect_sacrifice(board_before, move, mover_color):
        motifs.append("sacrifice")

    phenomenon = motifs[0] if motifs else "positional_decline"

    features = {
        "king_safety": _king_safety(board_after, loser_color),
        "development": _development(board_after, loser_color),
        "attack_pressure": round(max(0.0, min(1.0, loss_point.swing_against_loser / 800)), 3),
        "material_swing": round(max(-10.0, min(10.0, loss_point.swing_against_loser / 100)), 3),
    }

    severity = round(max(0.0, min(1.0, loss_point.swing_against_loser / 1000)), 3)

    return Signature(
        phenomenon=phenomenon,
        motifs=motifs,
        phase=_phase(board_before),
        features=features,
        severity=severity,
        ply=loss_point.ply,
    )
