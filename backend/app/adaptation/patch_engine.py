"""
Applies WeaknessRecord penalties to MultiPV candidates. This is the
piece that turns 'Mahoraga remembers' from a database row into actually
different play.

For each candidate move, we project two plies ahead (our candidate, then
the opponent's likely reply via a shallow search) before extracting a
signature through the real extract_signature pipeline, since stored
WeaknessRecords were themselves captured right after an opponent's
decisive move landed - comparing apples to apples requires matching that
shape, not just our own move in isolation.
"""
from __future__ import annotations

import chess

from app.adaptation.loss_localizer import LossPoint
from app.adaptation.signature_extractor import Signature, extract_signature
from app.adaptation.similarity import similarity
from app.models.db_models import WeaknessRecord

WATCHING_PENALTY = 30       # centipawns
ADAPTED_BASE_PENALTY = 150  # centipawns, scaled by confidence
REPLY_DEPTH = 6             # shallow - this runs once per candidate, keep it cheap


def _weakness_as_signature(rec: WeaknessRecord) -> Signature:
    return Signature(
        phenomenon=rec.phenomenon,
        motifs=rec.motifs,
        phase=rec.phase,
        features=rec.representative_features,
    )


def _project_candidate_signature(
    engine,
    board: chess.Board,
    move: chess.Move,
    mover_color: chess.Color,
) -> Signature:
    """
    Pushes our candidate move, then the opponent's likely best reply
    (shallow search - this isn't the real move, just a plausible one to
    project exposure against), then runs the same extract_signature used
    on real losses, with the mover as the loser_color, matching how real
    WeaknessRecords were captured.
    """
    board_after_us = board.copy(stack=False)
    board_after_us.push(move)

    if board_after_us.is_game_over():
        opponent_reply = None
    else:
        opponent_reply = engine.best_move(board_after_us, depth=REPLY_DEPTH)

    if opponent_reply is None:
        final_board_before = board_after_us
        final_move = move  # nothing to push further; signature reflects our move alone
        final_mover = mover_color
    else:
        final_board_before = board_after_us
        final_move = opponent_reply
        final_mover = not mover_color

    fake_loss = LossPoint(
        ply=board.fullmove_number,
        board_before=final_board_before,
        move=final_move,
        eval_before=0.0,   # unknown without a full re-eval; only used indirectly via swing below
        eval_after=0.0,
        swing_against_loser=0.0,  # unknown without a full re-eval; attack_pressure feature won't be informative here
        loser_color=mover_color,  # always Mahoraga - WeaknessRecords describe Mahoraga's own exposure
    )
    return extract_signature(fake_loss)


def rerank_candidates(
    engine,
    board: chess.Board,
    candidates: list[tuple[chess.Move, float]],
    active_weaknesses: list[WeaknessRecord],
    mover_color: chess.Color,
) -> list[tuple[chess.Move, float]]:
    """
    candidates: [(move, eval_cp_from_engine), ...] best first, from
    EngineWrapper.multipv_candidates(). Returns re-ranked list (still
    best first) after applying weakness-based penalties.
    """
    if not active_weaknesses:
        return candidates

    weakness_sigs = [(w, _weakness_as_signature(w)) for w in active_weaknesses]
    adjusted = []

    for move, cp in candidates:
        candidate_sig = _project_candidate_signature(engine, board, move, mover_color)
        penalty = 0.0
        for weakness, w_sig in weakness_sigs:
            sim = similarity(candidate_sig, w_sig)
            if sim is None:
                continue
            if weakness.status == "adapted":
                penalty = max(penalty, sim * weakness.confidence * ADAPTED_BASE_PENALTY)
            elif weakness.status == "watching":
                penalty = max(penalty, sim * weakness.confidence * WATCHING_PENALTY)
        # cp is White-relative. Penalty must push the score AWAY from
        # whoever is actually moving, regardless of color - so it's
        # subtracted for White (toward Black's favor) and added for
        # Black (toward White's favor), not always subtracted.
        signed_penalty = penalty if mover_color == chess.WHITE else -penalty
        adjusted.append((move, cp - signed_penalty, penalty))

    # Mahoraga playing as White wants max cp, as Black wants min cp (cp is white-relative from engine)
    adjusted.sort(key=lambda t: t[1], reverse=(mover_color == chess.WHITE))
    return [(m, cp) for m, cp, _ in adjusted]