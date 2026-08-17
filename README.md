# Mahoraga — Divine General of Adaptation (Adaptive Chess Agent)

> *"No matter what you do, it will adapt."* — inspired by the Divine General of Adaptation, **Mahoraga**, from *Jujutsu Kaisen*.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Mahoraga is an **adaptive chess opponent that learns from its losses** — just like the Shikigami it's named after. It starts weak and grows stronger by turning every beat into a lesson.

- 🎯 **Starts weak, auto-adjusts** — the more you beat it, the stronger it gets.
- 🧠 **Learns your weaknesses** — every loss becomes a *signature* (tactical motifs, phase, king-safety, development) and grows **confidence** when it sees the same shape again.
- ⚔️ **Adapts mid-game** — the **Wheel of Adaptation** turns: Mahoraga biases its move search away from positions matching its learned patterns, *without* touching Stockfish's raw strength.
- ♟️ **Chess.com-inspired UI** — clean two-column layout with a distraction-free board, 8-handled adaptation wheel, moves scroll table, captured pieces counter, and sound FX.
- 🌐 **100% local** — browser UI, FastAPI backend, SQLite, and Stockfish all run on your machine. No cloud, no accounts.

The full spec lives in [mahoraga-v1-technical-design.md](mahoraga-v1-technical-design.md).

---

## Why we need YOU

Mahoraga is being built in the open, and it needs **two kinds of people**:

1. **Chess players** — play it, break it, and tell us what feels wrong. Found a move that should have worked? A bot that seems to "know" too much or too little? **Open an issue** and paste the FEN (the game exports it in the board state) — your report becomes data that makes Mahoraga smarter.
2. **Developers** — build the bot, the UI, and the learning layer. The design deliberately separates the *chess engine* (Stockfish) from the *adaptation layer*, so contributors can dive into the AI without touching move search.

Everything you need is in [CONTRIBUTING.md](CONTRIBUTING.md).

---

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

Open http://127.0.0.1:8000 in a browser. You play White. Click a white piece, then click its destination square. Use the **New battle** button to reset the board. The header shows Mahoraga's current Elo and your head-to-head record so you can watch the wheel turn.

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
- Opening-specific memory (a learned book).
- Optional server mode so remote opponents can play.

## Contributing

This is an open-source project under the MIT license. Bug reports, feature ideas, documentation, and pull requests are all welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) to get started.
