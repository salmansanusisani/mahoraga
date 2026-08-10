# Mahoraga — build guide (A to Z)

This is an implementation guide, not a design discussion. It assumes the reader (human or AI coding agent) has the companion architecture doc (`mahoraga-v1-technical-design.md`) for *why* each piece exists, and needs this doc for *what to build, in what order, and how to know each phase is done*.

**Rule for whoever builds this: complete each phase's acceptance criteria before starting the next one. Phase 1 in particular is not optional or skippable — it's the whole risk of the project.**

---

## 0. Tech stack

**Backend**
- Python 3.11+
- FastAPI (REST API)
- `python-chess` (board state, PGN, legality)
- Stockfish binary via UCI (`python-chess`'s `chess.engine` module — no separate wrapper library needed)
- SQLModel + SQLite for development, swappable to Postgres later (same models, just change the connection string)
- `pytest` for tests

**Frontend**
- Vite + React + TypeScript
- `react-chessboard` for the board component
- Plain `fetch` calls to the backend REST API — no need for a heavier state library at v1 scale

**Why this stack:** everything here is a solved, boring problem except the adaptation engine itself. Don't spend novelty budget on infrastructure choices.

---

## 1. Repository layout

```
mahoraga/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models/
│   │   │   ├── db_models.py
│   │   │   └── schemas.py
│   │   ├── chess_engine/
│   │   │   ├── engine_wrapper.py
│   │   │   └── move_selector.py
│   │   ├── adaptation/
│   │   │   ├── loss_localizer.py
│   │   │   ├── signature_extractor.py
│   │   │   ├── similarity.py
│   │   │   ├── confidence.py
│   │   │   ├── patch_engine.py
│   │   │   └── weakness_memory.py
│   │   ├── profiling/
│   │   │   └── player_profile.py
│   │   └── api/
│   │       ├── routes_game.py
│   │       ├── routes_player.py
│   │       └── routes_adaptation.py
│   ├── tests/
│   │   ├── test_signature_extractor.py
│   │   ├── test_similarity.py
│   │   └── offline_harness/
│   │       ├── run_validation.py
│   │       └── fixtures/          # PGNs, one per known tactic/category
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── components/
    │   │   ├── Board.tsx
    │   │   ├── AdaptationWheel.tsx
    │   │   └── GameControls.tsx
    │   └── api/
    │       └── client.ts
    └── package.json
```

Create this skeleton in phase 0. Empty files are fine — they get filled in as each phase is built.

---

## 2. Phase 0 — environment setup

1. Install Stockfish locally (`apt install stockfish` / `brew install stockfish` / download binary). Confirm it runs: `stockfish` in a terminal should drop into a UCI prompt.
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install fastapi uvicorn python-chess sqlmodel pytest` → freeze into `backend/requirements.txt`
4. `npm create vite@latest frontend -- --template react-ts`, then `npm install react-chessboard`
5. Confirm `python -c "import chess.engine; e = chess.engine.SimpleEngine.popen_uci('stockfish'); print(e.id); e.quit()"` prints the Stockfish version. If this fails, nothing downstream will work — fix it before proceeding.

**Done when:** Stockfish is callable from Python, both project folders exist with the skeleton above, and `uvicorn app.main:app` (even with an empty `main.py` returning `{"status": "ok"}`) runs.

---

## 3. Phase 1 — offline validation harness (build this before anything else)

This phase has no game loop, no API, no frontend. It's a standalone script that proves the core idea works.

### 3.1 `chess_engine/engine_wrapper.py`
Minimal for this phase: a function that takes a `chess.Board` and returns Stockfish's evaluation (centipawns) and principal variation at a given depth. This is enough for loss localization; full MultiPV/skill-level control comes in phase 2.

### 3.2 `adaptation/loss_localizer.py`
Input: a full PGN of a lost game. Output: the ply index where evaluation collapsed. Implementation: walk the game move by move, evaluate each resulting position, find the largest single-move eval swing against the losing side.

### 3.3 `adaptation/signature_extractor.py`
Input: a `chess.Board` at the losing ply plus a few plies of context. Output: a `Signature` dict matching the schema in the architecture doc — `motifs` (list, from a fixed vocabulary: `fork`, `pin`, `skewer`, `back_rank`, `king_attack`, `discovered_attack`, `overloaded_defender`, `removed_defender`, `sacrifice`), `phase`, and the four continuous `features` (`king_safety`, `development`, `attack_pressure`, `material_swing`).

Concrete formulas to implement:
- `king_safety`: count of friendly pieces on squares adjacent to the king, divided by 8, penalized if the king hasn't castled
- `development`: fraction of minor pieces + queen that have left their starting square
- `attack_pressure`: normalized eval swing over the 2-3 plies before the loss (from 3.1's evaluator)
- `material_swing`: raw eval delta in pawns at the losing ply, clipped to [-10, 10]
- `motifs`: detect via simple rule checks against the board state and the Stockfish PV (e.g. a fork is detected if the PV's next move attacks two or more valuable pieces simultaneously)

### 3.4 `adaptation/similarity.py`
Implements the function from the architecture doc:
```
motif_overlap = jaccard(A.motifs, B.motifs)
feature_distance = normalized_euclidean(A.features, B.features)
similarity = 0.6 * motif_overlap + 0.4 * (1 - feature_distance)
```
Only compare signatures with the same `phase`. Expose both the raw score and the threshold check (`≥0.75 → same weakness`).

### 3.5 `tests/offline_harness/fixtures/`
Collect 30-50 PGNs of real or constructed losses, at least 5 variants each across 4-6 distinct categories (e.g. Scholar's Mate variants, knight fork traps, back-rank mates, queenside minority attacks). Label each fixture file with its intended category in the filename (`scholars_mate_01.pgn`, `knight_fork_03.pgn`, etc.) — this is your ground truth.

### 3.6 `tests/offline_harness/run_validation.py`
Loads every fixture, extracts a signature, computes the full pairwise similarity matrix, and reports:
- average similarity within each labeled category (should be ≥0.75)
- average similarity across different categories (should be <0.5)
- any individual pair that's badly misclassified

**Done when:** running `python run_validation.py` shows same-category pairs clustering above threshold and different-category pairs staying below it. If it doesn't, adjust the motif vocabulary, feature formulas, or similarity weights and rerun — do not proceed to phase 2 until this holds up. This is the actual R&D of the project; everything after this is standard engineering.

---

## 4. Phase 2 — playable core (CLI only, no adaptation yet)

1. Flesh out `engine_wrapper.py`: skill level (0-20), depth cap, and MultiPV support via `chess.engine`'s `configure()` and `analyse(multipv=N)`.
2. Write a bare CLI loop in a throwaway script: human enters UCI moves, engine responds at a fixed weak skill level, game gets saved as PGN to disk.
3. No adaptation logic touches this yet — the goal is just confirming you can reliably play a full legal game against a controllable-strength Stockfish.

**Done when:** you can play a full game start to finish from the terminal and the PGN is saved correctly.

---

## 5. Phase 3 — wire the adaptation loop into real play

1. `adaptation/confidence.py`: implement `confidence = occurrences / (occurrences + 2)` and the decay function (`confidence *= 0.95` per game without recurrence, archive below 0.25).
2. `adaptation/weakness_memory.py`: CRUD layer over a `WeaknessRecord` table (see schema in section 7). On a new signature: run similarity against existing records for this player and phase; merge if ≥0.75, else create new. Update `occurrences`, recompute `confidence`, set `status` (`watching` at 1 occurrence, `adapted` at 2+ with confidence past threshold).
3. `adaptation/patch_engine.py`: given a list of MultiPV candidate moves and the active WeaknessRecords for the player, project each candidate's resulting-position signature, compare against active records, apply a penalty (small for `watching`, larger and confidence-scaled for `adapted`), return the re-ranked list.
4. `chess_engine/move_selector.py`: glue — calls `engine_wrapper` for MultiPV candidates, calls `patch_engine` to re-rank, plays the top result.
5. After each game ends: run `loss_localizer` → `signature_extractor` → `weakness_memory.update()` automatically.

**Done when:** playing the same trap against the CLI bot twice in a row against the same player ID produces a visible status change from `watching` to `adapted` in the database, and the bot's third response to that trap is measurably different (check the patch_engine's penalty was actually applied to the winning candidate).

---

## 6. Phase 4 — backend API

Wrap the phase 3 game loop in FastAPI. Endpoint contract:

| Method | Path | Purpose |
|---|---|---|
| POST | `/players` | create a player, returns `player_id` |
| POST | `/games` | start a game for a player, returns `game_id` + initial board FEN |
| POST | `/games/{game_id}/move` | submit a player move (UCI or SAN), returns Mahoraga's reply move + updated FEN |
| GET | `/games/{game_id}` | current board state, move history |
| GET | `/players/{player_id}/profile` | style vector, estimated strength, win/loss record |
| GET | `/players/{player_id}/wheel` | the 8-category aggregate confidence data for the adaptation wheel |
| GET | `/players/{player_id}/weaknesses` | list of WeaknessRecords, for a "what Mahoraga has learned" screen |

Turn-based REST is sufficient for v1 — no need for WebSockets unless you later want live opponent-thinking indicators.

**Done when:** you can drive a full game through Postman/curl alone, with no frontend, and see WeaknessRecords update via the `/weaknesses` endpoint after a loss.

---

## 7. Database schema

```sql
CREATE TABLE player (
  id UUID PRIMARY KEY,
  created_at TIMESTAMP,
  estimated_strength INTEGER,
  games_played INTEGER DEFAULT 0,
  mahoraga_wins INTEGER DEFAULT 0,
  player_wins INTEGER DEFAULT 0,
  draws INTEGER DEFAULT 0,
  style_vector JSONB
);

CREATE TABLE game (
  id UUID PRIMARY KEY,
  player_id UUID REFERENCES player(id),
  pgn TEXT,
  result TEXT,
  started_at TIMESTAMP,
  ended_at TIMESTAMP
);

CREATE TABLE signature (
  id UUID PRIMARY KEY,
  player_id UUID REFERENCES player(id),
  game_id UUID REFERENCES game(id),
  phenomenon TEXT,
  motifs JSONB,
  phase TEXT,
  features JSONB,
  severity FLOAT,
  ply INTEGER,
  created_at TIMESTAMP
);

CREATE TABLE weakness_record (
  id UUID PRIMARY KEY,
  player_id UUID REFERENCES player(id),
  phenomenon TEXT,
  representative_features JSONB,
  matched_signature_ids JSONB,
  occurrences INTEGER DEFAULT 1,
  confidence FLOAT,
  status TEXT,               -- watching | adapted | archived
  last_seen_game_id UUID,
  last_seen_at TIMESTAMP,
  opponent_success_before FLOAT,
  opponent_success_after FLOAT
);
```

Start in SQLite (file-based, zero setup) with SQLModel; the model definitions are identical if you move to Postgres later, only the connection string in `db.py` changes.

---

## 8. Phase 5 — frontend

1. `Board.tsx`: `react-chessboard`, calls `POST /games/{id}/move` on each player move, updates from the FEN returned.
2. `AdaptationWheel.tsx`: pulls `GET /players/{id}/wheel`, renders the 8-handle wheel (reuse the SVG/JS structure already prototyped — radial spokes, opacity-based fill per category, rotate animation on update).
3. `GameControls.tsx`: new game button, shows post-game toast messages sourced from newly created/updated WeaknessRecords ("Weakness detected: early king-side attack") — this is the narrative "ritual of adaptation" moment, and it should read directly off real WeaknessMemory data, never a scripted line.
4. `App.tsx`: wires it together, holds `player_id` in local state (no auth needed for v1 — a single local player is fine to start).

**Done when:** a full game is playable in the browser, a loss visibly changes the wheel and produces a post-game message, and a second loss to the same tactic visibly plays out differently.

---

## 9. Phase 6 — the pieces from the architecture doc not yet covered

Build these once phases 1-5 are solid, not before:

- `profiling/player_profile.py`: style vector from the first 1-2 games (opening choice, blunder rate vs Stockfish eval, capture/sacrifice frequency)
- Signal-responsive acceleration in `engine_wrapper.py` / `move_selector.py`: mid-game strength bump if the player's opening moves are consistently near-optimal
- The measurable "fully adapted" check (section 0.1 of the architecture doc) as a background job or on-demand endpoint, triggering the wheel's full-spin UI state
- Effectiveness tracking: after a patch is applied, track whether the opponent's success rate against that phenomenon actually dropped, write to `opponent_success_before/after` on the WeaknessRecord

---

## 10. Notes for whichever AI agent builds this

- Work one phase at a time. Don't let a coding agent "helpfully" build the frontend before phase 1's harness passes — that's the exact trap this project needs to avoid.
- Phase 1's fixture PGNs are the ground truth for the whole system. If they're low-quality or too few, everything downstream inherits that weakness. Spend real effort here.
- Keep the chess-strength logic (Stockfish calls) and the adaptation logic (signature/similarity/patch) in separate modules with a clean interface between them, as laid out above — this is what lets you debug or improve one without touching the other, and it's the separation the architecture doc calls out as fundamental.
- Commit after each phase's "Done when" criteria are met, not mid-phase.
