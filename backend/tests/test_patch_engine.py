import uuid

import chess
from sqlmodel import Session

from app.adaptation.loss_localizer import LossPoint
from app.adaptation.patch_engine import _project_candidate_signature, rerank_candidates
from app.adaptation.signature_extractor import extract_signature
from app.adaptation.similarity import similarity
from app.adaptation.weakness_memory import update_from_signature
from app.db import engine


class FakeEngine:
    """Scripted reply per candidate move, so projection tests are deterministic."""

    def __init__(self, reply_map: dict[str, str]):
        self._reply_map = reply_map

    def best_move(self, board: chess.Board, depth: int) -> chess.Move | None:
        last = board.move_stack[-1]
        reply = self._reply_map.get(last.uci())
        return chess.Move.from_uci(reply) if reply else next(iter(board.legal_moves))


def _scholars_mate_board() -> chess.Board:
    board = chess.Board()
    for uci in ("e2e4", "e7e5", "d1h5", "b8c6", "f1c4"):
        board.push_uci(uci)
    return board


def _stored_signature() -> object:
    """The real pipeline's signature for this loss: White's Qxf7# is the
    decisive ply (largest swing), captured with loser_color=Black."""
    board = _scholars_mate_board()
    board.push_uci("g8f6")  # Black walks into the trap
    loss = LossPoint(
        ply=5,
        board_before=board.copy(stack=False),
        move=chess.Move.from_uci("h5f7"),  # Qxf7# - the decisive move
        eval_before=0.0,
        eval_after=1000.0,
        swing_against_loser=1000.0,
        loser_color=chess.BLACK,
    )
    return extract_signature(loss)


def test_projected_signature_matches_stored_loss() -> None:
    board = _scholars_mate_board()
    engine = FakeEngine({"g8f6": "h5f7", "g7g6": "d2d3"})
    stored = _stored_signature()

    blunder = _project_candidate_signature(engine, board, chess.Move.from_uci("g8f6"), chess.BLACK)
    defense = _project_candidate_signature(engine, board, chess.Move.from_uci("g7g6"), chess.BLACK)

    assert (similarity(blunder, stored) or 0) >= 0.75
    assert (similarity(defense, stored) or 0) < 0.75


def test_rerank_penalizes_matching_weakness() -> None:
    board = _scholars_mate_board()

    db = Session(engine)
    try:
        # Two losses on the same shape promote the record to "adapted",
        # which is when the patch engine begins applying its strong penalty.
        signature = _stored_signature()
        player_id = uuid.uuid4()
        update_from_signature(db, player_id, uuid.uuid4(), signature)
        record = update_from_signature(db, player_id, uuid.uuid4(), signature)
        assert record.status == "adapted"

        candidates = [
            (chess.Move.from_uci("g8f6"), -50.0),  # the blunder; same shape as the loss
            (chess.Move.from_uci("g7g6"), -20.0),  # safe defensive move
        ]
        fake = FakeEngine({"g8f6": "h5f7", "g7g6": "d2d3"})

        reranked = rerank_candidates(fake, board, candidates, [record], chess.BLACK)
        best = min(reranked, key=lambda item: item[1])
        assert best[0].uci() == "g7g6", reranked

        # Sanity: without a record the blunder would have stayed first.
        no_record = rerank_candidates(fake, board, candidates, [], chess.BLACK)
        assert no_record[0][0].uci() == "g8f6"
    finally:
        db.close()