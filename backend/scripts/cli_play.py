"""
Phase 2: bare CLI game loop. No adaptation logic touches this yet -
just proving a full legal game is playable against a strength-controlled
Stockfish, and that the PGN saves correctly.

Usage: python cli_play.py [skill_level]
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import chess
import chess.pgn
import datetime

from app.chess_engine.engine_wrapper import EngineWrapper


def play_game(human_moves_uci: list[str], skill_level: int = 0, depth: int = 5):
    """
    Drives a full game. human_moves_uci is consumed in order for the human
    side; Mahoraga (Stockfish at skill_level) plays the other side. Stops
    when human_moves_uci runs out or the game ends.
    """
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["Event"] = "Mahoraga phase 2 CLI test"
    game.headers["Date"] = datetime.date.today().isoformat()
    game.headers["White"] = "Human"
    game.headers["Black"] = f"Mahoraga (skill {skill_level})"
    node = game

    with EngineWrapper() as engine:
        engine.configure_strength(skill_level)
        move_idx = 0
        while not board.is_game_over() and move_idx < len(human_moves_uci):
            # human (white) move
            move = chess.Move.from_uci(human_moves_uci[move_idx])
            if move not in board.legal_moves:
                print(f"ILLEGAL human move {move} at ply {move_idx}, stopping")
                break
            board.push(move)
            node = node.add_variation(move)
            move_idx += 1
            print(f"Human played {move}, board fen: {board.fen()}")

            if board.is_game_over():
                break

            # Mahoraga (black) reply
            reply = engine.best_move(board, depth=depth)
            board.push(reply)
            node = node.add_variation(reply)
            print(f"Mahoraga (skill {skill_level}) replied {reply}")

    game.headers["Result"] = board.result() if board.is_game_over() else "*"
    return game, board


if __name__ == "__main__":
    skill = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    # a short, fully legal opening sequence for the human side
    human_moves = ["e2e4", "f1c4", "d1h5", "h5f7"]  # classic Scholar's Mate attempt, no blocking pieces
    game, final_board = play_game(human_moves, skill_level=skill, depth=5)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "tmp_games")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"cli_test_skill{skill}.pgn")
    with open(out_path, "w") as f:
        print(game, file=f)

    print(f"\nFinal FEN: {final_board.fen()}")
    print(f"Result: {game.headers['Result']}")
    print(f"PGN saved to {out_path}")
