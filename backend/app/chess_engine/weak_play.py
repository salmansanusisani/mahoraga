"""
Genuine weak play. Stockfish's own strength knobs can't get below ~1320
elo (UCI_Elo's hard floor) or reliably blunder even at Skill Level 0
(it still filters out catastrophic moves). Below that range, we build
weak play ourselves: rank every legal move by Stockfish's own eval, then
sample from that ranked list with a temperature that widens as target elo
drops. High elo -> sharp distribution, almost always the best move. Low
elo -> flat distribution, real chance of a genuine blunder (hanging a
piece, missing a mate, walking into a fork) - because the move is
actually sampled from the full legal-move distribution, not filtered
through Stockfish's own "never truly awful" floor the way Skill Level is.

This is a first-pass calibration (the ELO_TEMPERATURE_TABLE below), not
empirically validated against real rated play. Proper calibration would
mean running this selector in self-play or against known-rated bots and
adjusting the table until observed performance matches target elo -
worth doing before trusting the numbers, not assumed here.
"""
from __future__ import annotations

import math
import random

import chess

# elo -> temperature (centipawns). Higher temperature = flatter
# distribution = more likely to pick a bad move. Interpolated linearly
# between points; elo below/above the table clamps to the nearest end.
ELO_TEMPERATURE_TABLE = [
    (100, 220),
    (400, 140),
    (800, 70),
    (1000, 45),
    (1200, 25),
    (1320, 12),  # hands off to Stockfish's native UCI_Elo above this point
]

HANDOFF_ELO = 1320
MAX_CANDIDATES = 40  # cap MultiPV cost; legal moves rarely exceed this in practice

# Stockfish Skill Level -> approximate Elo (first-pass linear estimate of
# widely-cited pairs). Used to bridge the per-game skill_level (from the
# API) into the elo domain the weak/strong split lives in.
SKILL_ELO_TABLE = [
    (0, 1320), (1, 1384), (2, 1445), (3, 1502), (4, 1557), (5, 1620),
    (6, 1690), (7, 1764), (8, 1839), (9, 1912), (10, 1983), (11, 2056),
    (12, 2139), (13, 2232), (14, 2326), (15, 2405), (16, 2503),
    (17, 2580), (18, 2666), (19, 2759), (20, 2859),
]


def _interpolate(table: list[tuple[int, float]], value: int) -> float:
    if value <= table[0][0]:
        return table[0][1]
    if value >= table[-1][0]:
        return table[-1][1]
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x0 <= value <= x1:
            frac = (value - x0) / (x1 - x0)
            return y0 + frac * (y1 - y0)
    return table[-1][1]  # unreachable, satisfies type checkers


def temperature_for_elo(elo: int) -> float:
    return _interpolate(ELO_TEMPERATURE_TABLE, elo)


def skill_to_elo(skill_level: int) -> int:
    """Bridges the API's per-game Skill Level (0-20) into target Elo."""
    skill_level = max(0, min(20, skill_level))
    return round(_interpolate(SKILL_ELO_TABLE, skill_level))


def weak_move(engine, board: chess.Board, target_elo: int, depth: int = 4) -> chess.Move:
    """
    Samples a move from the full legal-move distribution, weighted by
    Stockfish eval and an elo-calibrated temperature. depth is kept
    shallow deliberately - weak play shouldn't come from a strong engine
    that merely "chooses" to be bad, it should come from genuinely limited
    lookahead plus sampling noise.
    """
    legal_count = board.legal_moves.count()
    if legal_count == 0:
        raise ValueError("no legal moves available")
    if legal_count == 1:
        return next(iter(board.legal_moves))

    n = min(legal_count, MAX_CANDIDATES)
    candidates = engine.multipv_candidates(board, depth=depth, n=n)
    if not candidates:
        return engine.best_move(board, depth=depth)

    mover_color = board.turn
    # candidates are (move, cp) White-relative; flip to mover-relative
    # so "higher is always better for whoever is about to move"
    scores = [(mv, cp if mover_color == chess.WHITE else -cp) for mv, cp in candidates]

    temperature = temperature_for_elo(target_elo)
    best_score = max(s for _, s in scores)
    # subtract best_score before exponentiating for numerical stability;
    # doesn't change the resulting probabilities, softmax is shift-invariant
    weights = [math.exp((s - best_score) / max(temperature, 1e-6)) for _, s in scores]
    total = sum(weights)
    probs = [w / total for w in weights]

    chosen = random.choices([mv for mv, _ in scores], weights=probs, k=1)[0]
    return chosen