"""
v2 fixture generator. Unlike v1 (full hand-typed games where the claimed
motif wasn't guaranteed to be at the peak eval-swing ply), each fixture
here starts from a custom FEN with the tactical move played directly,
so the intended motif is unambiguously at ply 0.
"""
import chess
import chess.pgn
import os

OUT = "/home/claude/mahoraga/backend/tests/offline_harness/fixtures"
os.makedirs(OUT, exist_ok=True)

# (filename, category, result, fen, uci_move)
CANDIDATES = [
    # --- fork: knight forks queen+rook (or two rooks), different squares/pieces ---
    ("fork_A_queen_rook", "fork", "1-0", "3q1r1k/8/8/8/3N4/8/8/6K1 w - - 0 1", "d4e6"),
    ("fork_B_queen_rook_alt_origin", "fork", "1-0", "3q1r1k/8/8/2N5/8/8/8/6K1 w - - 0 1", "c5e6"),
    ("fork_C_queen_bishop", "fork", "1-0", "3q1b1k/8/8/8/3N4/8/8/6K1 w - - 0 1", "d4e6"),
    ("fork_D_rook_rook", "fork", "1-0", "r3r2k/8/N7/8/8/8/8/6K1 w - - 0 1", "a6c7"),

    # --- back_rank: king trapped by own pawns, mate delivered different ways ---
    ("back_rank_A_rook_d_file", "back_rank", "1-0", "6k1/5ppp/8/8/8/8/8/3R2K1 w - - 0 1", "d1d8"),
    ("back_rank_B_rook_a_file", "back_rank", "1-0", "6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1", "a1a8"),
    ("back_rank_C_queen", "back_rank", "1-0", "6k1/5ppp/8/8/8/8/8/3Q2K1 w - - 0 1", "d1d8"),
    ("back_rank_D_rook_with_extra_piece", "back_rank", "1-0", "6k1/5ppp/8/8/8/2B5/8/3R2K1 w - - 0 1", "d1d8"),

    # --- pin: absolute pin against the king, undefended pinned piece ---
    ("pin_A_bishop_pins_knight", "pin", "1-0", "4k3/8/2n5/8/8/8/8/5B1K w - - 0 1", "f1b5"),
    ("pin_B_rook_pins_queen", "pin", "1-0", "4k3/8/4q3/8/8/8/8/R6K w - - 0 1", "a1e1"),
    ("pin_C_bishop_pins_knight_alt_origin", "pin", "1-0", "4k3/8/2n5/8/8/3B4/8/7K w - - 0 1", "d3b5"),

    # --- control: quiet, no tactic, minimal swing ---
    ("control_A_quiet_a3", "control", "1-0",
     "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 6 5", "a2a3"),
    ("control_B_quiet_h3", "control", "1-0",
     "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 6 5", "h2h3"),
    ("control_C_quiet_d3", "control", "1-0",
     "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 6 5", "d2d3"),
]

results = []
for fname, category, result, fen, uci in CANDIDATES:
    board = chess.Board(fen)
    game = chess.pgn.Game()
    game.setup(board)
    game.headers["Result"] = result
    game.headers["Event"] = category
    try:
        move = chess.Move.from_uci(uci)
        assert move in board.legal_moves, "illegal move"
        board.push(move)
        game.add_variation(move)
    except Exception as e:
        print(f"FAIL {fname}: {e}")
        results.append((fname, category, "FAIL"))
        continue
    path = os.path.join(OUT, fname + ".pgn")
    with open(path, "w") as f:
        print(game, file=f)
    results.append((fname, category, "OK"))
    print(f"OK   {fname}")

print("\nSummary:", sum(1 for r in results if r[2] == "OK"), "/", len(results), "fixtures built")
