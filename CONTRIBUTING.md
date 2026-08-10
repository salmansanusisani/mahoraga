# Contributing to Mahoraga — 八握剣・異戒神将

Thanks for wanting to help Mahoraga adapt. This project converts losses into
weakness signatures and biases Stockfish's move choice away from positions
that match known losing patterns. The design is documented in
[mahoraga-v1-technical-design.md](mahoraga-v1-technical-design.md).

**You don't have to be a programmer to contribute.** Chess players are just as
important as developers — your feedback is what trains the bot.

---

## For chess players: report what feels wrong

The best contributions you can make are **reports of real games** where
Mahoraga did something that felt wrong:

- Beat Mahoraga using the same idea more than once? Tell us — that means the
  adaptation layer didn't learn that weakness.
- Tried a move that the UI rejected as illegal, but it looked legal to you?
  Report it with the board position.
- Did the bot seem to "predict" your moves in an unfair way, or play absurdly
  weak late in a game? We want to hear about it.

### How to file a good bug report

1. **Reproduce** the situation as best you can.
2. **Open an issue** and include:
   - What you did (your move, or the opening you played).
   - What you expected to happen.
   - What actually happened.
   - **The board position (FEN)** if you can get it — it's the single most
     useful piece of data. It looks like
     `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`. You can copy
     it from the `fen` in the game's response, or just describe the board.
   - Optional: a screenshot.

No FEN? No problem — describe the position and the last few moves and we'll
figure it out.

---

## For developers: getting started

1. Fork the repository and clone your fork.
2. Follow the setup steps in [README.md](README.md) to install Python, Stockfish, and the dependencies.
3. Confirm you can run the tests:

```powershell
pytest
```

4. Create a feature branch:

```powershell
git checkout -b my-feature
```

## How to contribute

- **Report a bug** — open an issue with the board position (FEN), the move you
  tried, and what the app did.
- **Suggest an improvement** — open an issue describing the behavior you want.
- **Write code** — pick an issue, assign it to yourself (or mention it in a
  comment), and submit a pull request.
- **Improve docs** — the design and build guides are just markdown.

## Pull request guidelines

- Keep changes focused. One PR should do one thing.
- Add or update tests in `backend/tests/` for any behavior change, and run the
  full suite with `pytest` before pushing.
- For the offline validation, run:

```powershell
py -m tests.offline_harness.run_validation
```

- Follow the existing code style: short functions, type hints on Python
  signatures, no comments unless they explain a non-obvious decision.
- Never commit `.env` files, `*.db` files, or Stockfish binaries. The
  `.gitignore` already excludes them.

## Code map

- `backend/app/api/` — FastAPI routes (players, games, adaptation).
- `backend/app/adaptation/` — the learning layer: loss localization, signature
  extraction, similarity, weakness memory, and the patch engine that biases
  move selection.
- `backend/app/chess_engine/` — Stockfish wrapper and skill-based move
  selection.
- `backend/app/static/` — the browser UI (vanilla JS, no build step).
- `backend/tests/` — pytest suite and the offline validation harness.

## Questions

Open a discussion or issue on GitHub and someone will get back to you.
