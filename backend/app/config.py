"""Runtime configuration. Environment variables override safe local defaults."""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv("MAHORAGA_DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'mahoraga.db'}")
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH")


def stockfish_candidates() -> list[Path]:
    """Known Windows locations, the Linux location used by the original tests,
    and any Stockfish downloaded into the current user's Downloads folder."""
    configured = [Path(STOCKFISH_PATH).expanduser()] if STOCKFISH_PATH else []
    candidates = configured + [
        Path(r"C:\\Program Files\\Stockfish\\stockfish.exe"),
        Path(r"C:\\Program Files\\Stockfish\\stockfish-windows-x86-64-avx2.exe"),
        Path(r"C:\\Tools\\stockfish\\stockfish.exe"),
        Path("/usr/games/stockfish"),
    ]
    downloads = Path.home() / "Downloads"
    if downloads.is_dir():
        candidates += [
            path
            for pattern in ("stockfish-windows-x86-64-*/stockfish/*.exe", "stockfish-windows-x86-64-*/stockfish.exe")
            for path in downloads.glob(pattern)
        ]
    return candidates
