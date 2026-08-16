import random

import chess

from app.chess_engine.weak_play import (
    HANDOFF_ELO,
    skill_to_elo,
    temperature_for_elo,
    weak_move,
)


class StubEngine:
    """Cheap stand-in: every candidate gets an equal eval, so weak_move's
    sampling is uniform over the candidate pool."""

    def multipv_candidates(self, board, depth: int, n: int):
        return [(mv, 0.0) for mv in list(board.legal_moves)[:n]]

    def best_move(self, board, depth: int):
        return next(iter(board.legal_moves))


def test_temperature_table_is_monotonic_and_clamped() -> None:
    lo = temperature_for_elo(50)
    hi = temperature_for_elo(5000)
    assert lo == 220.0  # clamps to the cold end
    assert hi == 12.0  # clamps to the hot end
    samples = [temperature_for_elo(e) for e in (200, 500, 900, 1100, 1300)]
    assert all(a >= b for a, b in zip(samples, samples[1:]))
    assert abs(temperature_for_elo(1000) - 45.0) < 1e-6


def test_skill_to_elo_bridge() -> None:
    assert skill_to_elo(0) == HANDOFF_ELO
    assert skill_to_elo(20) == 2859
    assert skill_to_elo(10) == 1983
    assert skill_to_elo(-5) == HANDOFF_ELO  # clamped below
    assert skill_to_elo(99) == 2859  # clamped above


def test_weak_move_returns_legal_move() -> None:
    random.seed(7)
    board = chess.Board()
    move = weak_move(StubEngine(), board, target_elo=600, depth=2)
    assert move in board.legal_moves
