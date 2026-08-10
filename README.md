# Mahoraga — adaptive chess agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Mahoraga is an adaptive chess opponent that learns from its losses. Instead of
just searching for the strongest move, it answers a second question: *"why did
this player beat me, have I seen this shape before, and how much should that
change what I do now?"*

- Starts weak and **auto-adjusts** — the more you beat it, the stronger it gets.
- Records each loss as a **weakness signature** (motifs, phase, king-safety and
  development features) and grows **confidence** in patterns it sees again.
- **Biases its move search** away from positions matching high-confidence
  patterns, without touching Stockfish's raw strength.
- Runs 100% locally: browser UI, FastAPI backend, SQLite, and Stockfish all on
  your machine.

The full spec is in [mahoraga-v1-technical-design.md](mahoraga-v1-technical-design.md).

## Windows setup

1. Install Python 3.11 or newer from https://www.python.org/downloads/windows/ and select **Add Python to PATH**.
2. Download the Windows Stockfish executable from https://stockfishchess.org/download/ and extract it. If you leave it in `Downloads` (e.g. `Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe`) Mahoraga finds it automatically; otherwise set `STOCKFISH_PATH` to its full path.
3. In PowerShell:

```powershell
cd <repo>\backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` once, then activate again.

Open http://127.0.0.1:8000 in a browser. You play White. Click a white piece, then click its destination square. Use the New game button to reset the board. The header shows Mahoraga's current Elo and your head-to-head record so you can watch him adapt.

## Tests and validation

With the virtual environment active:

```powershell
pytest
py -m tests.offline_harness.run_validation
```

The validation command checks whether the Phase 1 loss signatures cluster the labeled tactical fixtures as designed. The app creates `backend\mahoraga.db` automatically on first start; delete only that file if you intentionally want to reset local player history.

## Roadmap

- More weakness phenomena: pawn structure, space, endgame technique.
- Per-opponent adaptation that scales to many players.
- Opening-specific memory (learned book).
- Optional server mode so remote opponents can play.

## Contributing

This is an open-source project under the MIT license. Bug reports, feature
ideas, documentation, and pull requests are all welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md) to get started.
