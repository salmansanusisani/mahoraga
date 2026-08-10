import chess
import chess.pgn
import os

OUT = "/home/claude/mahoraga/backend/tests/offline_harness/fixtures"
os.makedirs(OUT, exist_ok=True)

# (filename, category_label, result, list of SAN moves)
CANDIDATES = [
    # --- king_attack / Scholar's Mate family: same motif, different move order ---
    ("king_attack_01_scholars_classic", "king_attack", "1-0",
     "e4 e5 Qh5 Nc6 Bc4 Nf6 Qxf7#".split()),
    ("king_attack_02_bishop_first", "king_attack", "1-0",
     "e4 e5 Bc4 Nc6 Qh5 Nf6 Qxf7#".split()),
    ("king_attack_03_black_bishop_dev", "king_attack", "1-0",
     "e4 e5 Bc4 Bc5 Qh5 Nf6 Qxf7#".split()),
    ("king_attack_04_queen_first_bishop_dev", "king_attack", "1-0",
     "e4 e5 Qh5 Bc5 Bc4 Nf6 Qxf7#".split()),

    # --- fork: different shape, a real named trap involving a knight fork sac ---
    ("fork_01_fried_liver", "fork", "1-0",
     "e4 e5 Nf3 Nc6 Bc4 Nf6 Ng5 d5 exd5 Nxd5 Nxf7 Kxf7 Qf3+ Ke6 Nc3".split()),
    ("fork_02_simple_knight_fork", "fork", "1-0",
     "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 d6 O-O Bg4 c3 Nf6 d4 b5 Bb3 Nxd4 Nxd4 exd4 Qxg4".split()),

    # --- back_rank: constructed simple mate pattern ---
    ("back_rank_01_rook_mate", "back_rank", "1-0",
     "d4 d5 Nf3 Nf6 e3 e6 Bd3 c5 O-O Nc6 c3 Bd6 Nbd2 O-O Re1 Qc7 e4 dxe4 Nxe4 Nxe4 Bxe4 h6 Bd3 Re8 Qc2 f5 Rxe6 Rxe6 Bc4 Kh8 Bxe6".split()),
    ("back_rank_02_queen_infiltration", "back_rank", "1-0",
     "d4 Nf6 c4 e6 Nc3 Bb4 e3 O-O Bd3 d5 Nf3 c5 O-O Nc6 a3 Bxc3 bxc3 dxc4 Bxc4 Qc7 Bd3 e5 Qc2 Re8 Re1 e4 Bxe4 Nxe4 Qxe4 Bf5 Qh4 Rxe1 Rxe1 Bxb1".split()),

    # --- control: quiet positional loss, no sharp tactic, should NOT cluster with above ---
    ("control_01_positional_squeeze", "control", "1-0",
     "d4 d5 c4 e6 Nc3 Nf6 Bg5 Be7 e3 O-O Nf3 h6 Bh4 b6 Bxf6 Bxf6 cxd5 exd5 Qb3 c6 Bd3 Be6 O-O Nd7 Rfe1 Re8 e4 dxe4 Nxe4 Bxd4".split()),
    ("control_02_endgame_zugzwang", "control", "1-0",
     "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O h3 Nb8 d4 Nbd7 Nbd2 Bb7 Bc2 Re8 Nf1 Bf8 Ng3 g6 a4 c5 d5 c4".split()),
]

results = []
for fname, category, result, sans in CANDIDATES:
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["Result"] = result
    game.headers["Event"] = category
    node = game
    ok = True
    for i, san in enumerate(sans):
        try:
            move = board.parse_san(san)
            board.push(move)
            node = node.add_variation(move)
        except Exception as e:
            print(f"FAIL {fname} at move {i+1} ('{san}'): {e}")
            ok = False
            break
    if ok:
        path = os.path.join(OUT, fname + ".pgn")
        with open(path, "w") as f:
            print(game, file=f)
        results.append((fname, category, "OK", board.fen()))
        print(f"OK   {fname}  final_fen={board.fen()}")
    else:
        results.append((fname, category, "FAIL", None))

print("\nSummary:", sum(1 for r in results if r[2]=="OK"), "/", len(results), "fixtures built")
