import uuid

import chess
from sqlmodel import Session

from app.adaptation.loss_localizer import LossPoint
from app.adaptation.patch_engine import projected_signature, rerank
from app.adaptation.signature_extractor import extract_signature
from app.adaptation.weakness_memory import update_from_signature
from app.db import engine


def test_projected_signature_matches_black_loss() -> None:
    # Mahoraga (Black) just played the scholar's-mate blunder Nf6 against
    # Qh5+Bc4. The WeaknessRecord for that game describes BLACK's weakness.
    board = chess.Board()
    for uci in ("e2e4", "e7e5", "d1h5", "b8c6", "f1c4"):
        board.push_uci(uci)
    losing = board.copy()
    losing.push_uci("g8f6")
    loss = LossPoint(
        ply=5,
        board_before=board.copy(),
        move=chess.Move.from_uci("g8f6"),
        eval_before=0.0,
        eval_after=-1000.0,
        swing_against_loser=1000.0,
        loser_color=chess.BLACK,
    )
    signature = extract_signature(loss)

    # Candidate moves from the position Black faces before blundering.
    board = chess.Board()
    for uci in ("e2e4", "e7e5", "d1h5", "b8c6", "f1c4"):
        board.push_uci(uci)
    blunder = projected_signature(board, chess.Move.from_uci("g8f6"))
    defense = projected_signature(board, chess.Move.from_uci("g7g6"))

    from app.adaptation.similarity import similarity

    assert (similarity(blunder, signature) or 0) >= 0.75
    assert (similarity(defense, signature) or 0) < 0.75


def test_rerank_penalizes_matching_weakness() -> None:
    board = chess.Board()
    for uci in ("e2e4", "e7e5", "d1h5", "b8c6", "f1c4"):
        board.push_uci(uci)

    # Build the weakness record exactly the way the API does after a loss.
    db = Session(engine)
    try:
        loss_board = board.copy()
        loss_board.push_uci("g8f6")
        loss = LossPoint(
            ply=5,
            board_before=board.copy(),
            move=chess.Move.from_uci("g8f6"),
            eval_before=0.0,
            eval_after=-1000.0,
            swing_against_loser=1000.0,
            loser_color=chess.BLACK,
        )
        player_id = uuid.uuid4()
        signature = extract_signature(loss)
        # A second loss on the same shape promotes the record to "adapted",
        # which is when the patch engine begins applying its strong penalty.
        update_from_signature(db, player_id, uuid.uuid4(), signature)
        record = update_from_signature(db, player_id, uuid.uuid4(), signature)
        assert record.status == "adapted"

        candidates = [
            (chess.Move.from_uci("g8f6"), -50.0),  # the blunder; same shape as the loss
            (chess.Move.from_uci("g7g6"), -20.0),  # safe defensive move
        ]
        reranked = rerank(board, candidates, [record])
        best = min(reranked, key=lambda item: item[1])
        assert best[0].uci() == "g7g6", reranked

        # Sanity: without a record the blunder would have stayed first.
        no_record = rerank(board, candidates, [])
        assert no_record[0][0].uci() == "g8f6"
    finally:
        db.close()
