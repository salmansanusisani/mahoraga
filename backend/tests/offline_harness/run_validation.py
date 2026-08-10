"""
Phase 1 acceptance test. Loads every labeled fixture PGN, extracts a
signature for its localized loss, computes pairwise similarity, and
reports whether same-category pairs cluster above threshold while
different-category pairs stay below it.

Run: python run_validation.py
"""
from __future__ import annotations

import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import chess.pgn

from app.chess_engine.engine_wrapper import EngineWrapper
from app.adaptation.loss_localizer import localize_loss
from app.adaptation.signature_extractor import extract_signature
from app.adaptation.similarity import similarity, SIMILARITY_THRESHOLD

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


KNOWN_CATEGORIES = ["back_rank", "king_attack", "fork", "pin", "control"]


def category_of(filename: str) -> str:
    base = os.path.basename(filename)
    for cat in KNOWN_CATEGORIES:
        if base.startswith(cat):
            return cat
    return base.split(".")[0]


def load_fixtures():
    fixtures = []
    for path in sorted(glob.glob(os.path.join(FIXTURES_DIR, "*.pgn"))):
        with open(path) as f:
            game = chess.pgn.read_game(f)
        fixtures.append((category_of(path), os.path.basename(path), game))
    return fixtures


def main():
    fixtures = load_fixtures()
    print(f"Loaded {len(fixtures)} fixtures\n")

    signatures = []
    with EngineWrapper() as engine:
        for category, name, game in fixtures:
            loss = localize_loss(game, engine)
            if loss is None:
                print(f"SKIP {name}: no clear loser")
                continue
            sig = extract_signature(loss)
            signatures.append((category, name, sig))
            print(
                f"{name:45s} cat={category:12s} phenomenon={sig.phenomenon:10s} "
                f"motifs={sig.motifs} phase={sig.phase} sev={sig.severity}"
            )

    print("\n--- pairwise similarity ---\n")
    same_cat_scores = []
    diff_cat_scores = []

    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            cat_a, name_a, sig_a = signatures[i]
            cat_b, name_b, sig_b = signatures[j]
            sim = similarity(sig_a, sig_b)
            if sim is None:
                continue
            tag = "SAME" if cat_a == cat_b else "diff"
            print(f"[{tag}] {name_a:35s} vs {name_b:35s} sim={sim}")
            if cat_a == cat_b:
                same_cat_scores.append(sim)
            else:
                diff_cat_scores.append(sim)

    print("\n--- summary ---")
    if same_cat_scores:
        avg_same = sum(same_cat_scores) / len(same_cat_scores)
        print(f"Same-category pairs: {len(same_cat_scores)}, avg similarity = {avg_same:.3f} "
              f"(target >= {SIMILARITY_THRESHOLD})")
    else:
        print("No comparable same-category pairs found.")

    if diff_cat_scores:
        avg_diff = sum(diff_cat_scores) / len(diff_cat_scores)
        print(f"Different-category pairs: {len(diff_cat_scores)}, avg similarity = {avg_diff:.3f} "
              f"(target < 0.5)")
    else:
        print("No comparable different-category pairs found.")


if __name__ == "__main__":
    main()
