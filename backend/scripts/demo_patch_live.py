"""Live demo: the patch engine changes Mahoraga's move after it learns
a weakness. Uses the real Stockfish and the real DB record flow.

Run: python scripts/demo_patch_live.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import random
import uuid

import chess
from sqlmodel import Session

from app.adaptation.loss_localizer import LossPoint
from app.adaptation.signature_extractor import extract_signature
from app.adaptation.weakness_memory import update_from_signature
from app.chess_engine.engine_wrapper import EngineWrapper
from app.chess_engine.move_selector import select_move
from app.db import engine


def _build_adapted_record(db: Session):
    board = chess.Board()
    for uci in ("e2e4", "e7e5", "d1h5", "b8c6", "f1c4"):
        board.push_uci(uci)
    before = board.copy()
    board.push_uci("g8f6")  # the Scholar's-Mate blunder
    loss = LossPoint(
        ply=5, board_before=before, move=chess.Move.from_uci("g8f6"),
        eval_before=0.0, eval_after=-1000.0, swing_against_loser=1000.0,
        loser_color=chess.BLACK,
    )
    signature = extract_signature(loss)
    player_id = uuid.uuid4()
    update_from_signature(db, player_id, uuid.uuid4(), signature)
    record = update_from_signature(db, player_id, uuid.uuid4(), signature)
    assert record.status == "adapted"
    return player_id, record


def main():
    random.seed(7)
    board = chess.Board()
    for uci in ("e2e4", "e7e5", "d1h5", "b8c6", "f1c4"):
        board.push_uci(uci)
    print(f"Position after 1.e4 e5 2.Qh5 Nc6 3.Bc4 (Black = Mahoraga to move)")
    print(f"Threat: Qxf7# next move unless Black defends.\n")

    with Session(engine) as db:
        player_id, record = _build_adapted_record(db)
        with EngineWrapper() as engine_wrapper:
            before = select_move(engine_wrapper, board, [], skill_level=14)
            print(f"Before learning:  Mahoraga plays {before}")

            after = select_move(engine_wrapper, board, [record], skill_level=14)
            print(f"After learning:   Mahoraga plays {after}")

            if after.uci() == "g8f6":
                print("\nFATAL: Mahoraga still blundered into the learned trap.")
                sys.exit(1)
            print(f"\nOK: after learning the weakness, Mahoraga avoids the losing "
                  f"pattern ({after} instead of Nf6).")


if __name__ == "__main__":
    main()
