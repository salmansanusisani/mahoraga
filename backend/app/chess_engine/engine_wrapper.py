"""Stockfish UCI wrapper used by analysis and the playable game."""
from __future__ import annotations

from pathlib import Path
import shutil

import chess
import chess.engine

from app.config import stockfish_candidates

DEFAULT_DEPTH = 12
MATE_SCORE_CP = 10_000


def find_stockfish() -> str:
    for candidate in stockfish_candidates():
        if candidate.is_file():
            return str(candidate)
    for command in ("stockfish", "stockfish.exe"):
        found = shutil.which(command)
        if found:
            return found
    raise FileNotFoundError(
        "Stockfish was not found. Install it, then set STOCKFISH_PATH to its .exe file."
    )


class EngineWrapper:
    def __init__(self, path: str | None = None):
        self._engine = chess.engine.SimpleEngine.popen_uci(path or find_stockfish())

    @staticmethod
    def _score(info: dict) -> float:
        score = info["score"].white()
        if score.is_mate():
            return float(MATE_SCORE_CP if score.mate() > 0 else -MATE_SCORE_CP)
        return float(score.score() or 0)

    def evaluate_cp(self, board: chess.Board, depth: int = DEFAULT_DEPTH) -> float:
        return self._score(self._engine.analyse(board, chess.engine.Limit(depth=depth)))

    def principal_variation(self, board: chess.Board, depth: int = DEFAULT_DEPTH) -> list[chess.Move]:
        return self._engine.analyse(board, chess.engine.Limit(depth=depth)).get("pv", [])

    def configure_strength(self, skill_level: int = 5) -> None:
        self._engine.configure({"Skill Level": max(0, min(20, skill_level))})

    def best_move(self, board: chess.Board, depth: int = DEFAULT_DEPTH) -> chess.Move:
        return self._engine.play(board, chess.engine.Limit(depth=depth)).move

    def multipv_candidates(self, board: chess.Board, depth: int = DEFAULT_DEPTH, n: int = 5) -> list[tuple[chess.Move, float]]:
        infos = self._engine.analyse(board, chess.engine.Limit(depth=depth), multipv=n)
        if isinstance(infos, dict):
            infos = [infos]
        return [(info["pv"][0], self._score(info)) for info in infos if info.get("pv")]

    def close(self) -> None:
        self._engine.quit()

    def __enter__(self) -> "EngineWrapper":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
