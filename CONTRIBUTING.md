# Contributing to Mahoraga

Thanks for wanting to help Mahoraga learn and grow. This project converts
losses into weakness signatures and biases Stockfish's move choice away from
positions that match known losing patterns. The design is documented in
[mahoraga-v1-technical-design.md](mahoraga-v1-technical-design.md).

## Getting started

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
