# Mahoraga v1 — Technical Design

## The invention, in one sentence

An adaptive chess agent that converts losses into generalized weakness signatures, tracks confidence in those signatures per opponent, and biases its move search away from positions matching high-confidence signatures — without touching the underlying chess engine's raw strength.

Stockfish answers "what's the strongest move." Mahoraga answers "why did this player beat me, have I seen this shape before, and how much should that change what I do now." This document is the spec for the second question, since the first one is already solved by Stockfish.

## Build order (non-negotiable)

Validate the signature/similarity system on a static dataset of losses **before** writing a single line of game-loop or UI code. If it can't correctly cluster "same weakness, different move order" while keeping unrelated weaknesses separate, nothing downstream matters.

```
Loss dataset → Signature extraction → Similarity test → Does it cluster correctly?
                                                            /            \
                                                          NO             YES
                                                           │               │
                                                     fix the function   proceed to
                                                                        game loop
```

---

## 0. The agentic loop

This is the frame everything else sits inside, and it's worth stating explicitly rather than leaving implicit in the module list:

```
OBSERVE            — during the game (GameObserver, plus in-game signal check, see 0.2)
        │
        ▼
ANALYZE / REASON    — after the game ends (LossLocalizer → SignatureExtractor →
                       SimilarityEngine → WeaknessMemory update)
        │
        ▼
PLAN                — WeaknessMemory decides which records are watching vs adapted,
                       PatchEngine prepares the penalties that will apply next game
        │
        ▼
ACT                 — next game (MoveSelector, Stockfish + PatchEngine together)
        │
        ▼
REFLECT             — effectiveness tracking: did opponent success rate against
                       this phenomenon actually drop? feeds back into confidence/decay
        │
        └──────────────────────────────────────────────────────► back to OBSERVE
```

The reflect step is what makes this a loop instead of a pipeline. Without it, Mahoraga applies patches and never checks whether they worked — reflect is what lets a bad patch get corrected instead of sitting there forever.

### 0.1 Fully adapted — a measurable definition

Rather than a vague narrative moment, define it as a threshold the system can actually check:

- ≥90% of the player's recorded WeaknessRecords have reached `adapted` status with confidence ≥0.85, **and**
- Mahoraga's win rate against this player exceeds a set bar (e.g. 70%) over the trailing 10-game window, **and**
- effectiveness tracking shows opponent success rate against top recorded phenomena has measurably declined, not just that patches exist

All three, not just one — a single lucky streak shouldn't trigger the "domain expansion" moment, and neither should a pile of unused patches with no evidence they work.

### 0.2 Signal-responsive acceleration (for strong opponents)

The StrengthController shouldn't wait until between games to react. During the opening moves of game 1, compare the player's moves against Stockfish's own evaluation of move quality. If the first several moves are consistently near-optimal (book-quality opening, no measurable inaccuracies), treat that as a strength signal and raise the StrengthController's base level mid-game rather than making a grandmaster grind through a full 100-elo game before Mahoraga catches up. This only adjusts the floor (Layer 1 strength), not the adaptation memory — it's a fast, coarse correction, separate from the slower per-weakness patching described below.

## 1. Data model

### Signature
The core unit of the whole system. Produced once per meaningful loss/near-loss.

```json
{
  "signature_id": "uuid",
  "player_id": "uuid",
  "phenomenon": "king_attack",
  "motifs": ["early_queen", "bishop_battery", "weak_f7"],
  "phase": "opening",
  "features": {
    "king_safety": 0.28,
    "development": 0.42,
    "attack_pressure": 0.91,
    "material_swing": -6.2
  },
  "severity": 0.94,
  "source_game_id": "uuid",
  "ply": 7,
  "created_at": "timestamp"
}
```

- `motifs`: multi-hot tags from a fixed vocabulary (fork, pin, skewer, back_rank, king_attack, discovered_attack, overloaded_defender, removed_defender, sacrifice, ...). Detected against the Stockfish principal variation at the losing ply, not hand-labeled.
- `phase`: opening / middlegame / endgame. **Gates comparison** — signatures from different phases are never compared against each other.
- `features`: continuous, each 0-1 (material_swing excluded, see below):
  - `king_safety` = pawn-shield integrity + defender count on squares adjacent to king, normalized
  - `development` = fraction of minor pieces + queen that have moved off the back rank, at time of loss
  - `attack_pressure` = normalized Stockfish eval swing over the 2-3 plies leading to the loss
  - `material_swing` = raw eval delta in pawns, clipped to [-10, 10], kept separate from the 0-1 block since it's used differently (severity weighting, not similarity)
- `severity`: how bad the loss was (mate vs material loss vs positional damage), used to prioritize which signatures get processed first, not part of similarity.

### WeaknessRecord
One per confirmed-or-suspected recurring weakness for a given player. Signatures get matched into these.

```json
{
  "weakness_id": "uuid",
  "player_id": "uuid",
  "phenomenon": "king_attack",
  "representative_features": { "...": "running average of matched signatures' features" },
  "matched_signature_ids": ["uuid", "uuid"],
  "occurrences": 2,
  "confidence": 0.66,
  "status": "adapted",
  "last_seen_game_id": "uuid",
  "last_seen_at": "timestamp",
  "effectiveness": {
    "opponent_success_before": 0.78,
    "opponent_success_after": 0.31
  }
}
```

- `status`: `watching` (occurrences=1) → `adapted` (occurrences≥2 and confidence crosses threshold) → can decay back to `watching` or be archived if confidence drops too low.
- `effectiveness`: tracked after the patch goes live — did the opponent's success rate against this phenomenon actually drop? This is what tells you a patch is working, not just that it exists.

### PlayerProfile
```json
{
  "player_id": "uuid",
  "games_played": 37,
  "estimated_strength": 1730,
  "style_vector": {
    "tactical_aggression": 0.87,
    "risk_tolerance": 0.81,
    "opening_preparation": 0.64,
    "endgame_strength": 0.52,
    "king_attack_frequency": 0.88
  },
  "weakness_ids": ["uuid", "uuid", "uuid"],
  "record": { "mahoraga_wins": 21, "player_wins": 12, "draws": 4 }
}
```

Built per-player (not global, for v1 — see decision below), seeded from the first 1-2 games, refined continuously.

---

## 2. The similarity function

Given two signatures A and B **in the same phase**:

```
motif_overlap   = |A.motifs ∩ B.motifs| / |A.motifs ∪ B.motifs|      (Jaccard)
feature_distance = normalized_euclidean(A.features, B.features)      (0 = identical, 1 = max distance)

similarity = 0.6 * motif_overlap + 0.4 * (1 - feature_distance)
```

Threshold: `similarity ≥ 0.75` → same underlying weakness, merge into the same WeaknessRecord (update its running-average features, increment occurrences).
`0.5 ≤ similarity < 0.75` → flag for manual/logged review during development; don't auto-merge yet.
`< 0.5` → distinct weakness, new WeaknessRecord.

These weights and threshold are starting points, not gospel — this is exactly what the offline validation harness (section 5) is for: run it against real labeled loss data and tune the weights until clustering matches human judgment of "same weakness."

## 3. Confidence and decay

```
confidence = occurrences / (occurrences + k)      k = 2 (tunable)

occurrences=1 → confidence ≈ 0.33 → status: watching
occurrences=2 → confidence ≈ 0.66 → status: adapted
occurrences=4 → confidence ≈ 0.80
```

Decay, applied once per game the player plays where this weakness does **not** recur:

```
confidence *= 0.95
```

If confidence drops below ~0.25, archive the WeaknessRecord (stop applying its patch). This prevents indefinite accumulation of patches from one-off flukes and lets Mahoraga "forget" things that turned out not to be real patterns — directly addressing the failure mode where an adaptive bot turns into an overcautious tangle of special cases.

## 4. Patch application (how a signature changes a move)

1. At move time, run Stockfish with MultiPV to get the top N candidate moves (N≈5).
2. For each candidate, project the resulting position's features (same extractor used for signatures) as if the opponent responds with their most natural reply.
3. Compare that projected signature against all `active` (watching or adapted) WeaknessRecords for this player, same phase.
4. If similarity ≥ threshold against any record, apply a penalty to that candidate's score:
   - `watching` status → small penalty (nudge, e.g. -0.1 to -0.3 pawns equivalent)
   - `adapted` status → larger penalty scaled by confidence (e.g. -0.5 to -2.0 pawns equivalent)
5. Re-rank candidates by adjusted score, play the top one.

This keeps Stockfish's actual chess judgment intact — Mahoraga never plays an objectively terrible move to "prove" it adapted. It just deprioritizes moves that walk back into a known-bad shape, in proportion to how confident it is that shape is dangerous.

## 5. Offline validation harness (build this first)

Before any game loop exists:

1. Collect or generate a batch of PGN losses covering known tactical/strategic categories (Scholar's Mate variants, knight forks, back-rank mates, queenside minority attacks, etc.), several move-order variants per category.
2. Run signature extraction on each.
3. Run pairwise similarity across the whole batch.
4. Check: do same-category losses cluster together (similarity ≥ 0.75)? Do different-category losses stay separate?
5. Tune motif vocabulary, feature formulas, and similarity weights until this holds up against a hand-labeled ground truth set.

This is the actual R&D of the project. Everything after this point (game loop, patch application, UI) is comparatively standard engineering.

## 6. Scope decision: per-player, not global (v1)

Confirmed direction: each player gets their own PlayerProfile and WeaknessRecords. "Mahoraga remembers you" is the stronger and more testable product promise, and it avoids the harder problem of merging weakness records discovered by very different playstyles into one coherent global model. A global mode (anonymized, validated adaptations shared across all players) is a legitimate v2/v3 feature, not a v1 concern.

## 7. Module list

```
GameObserver          — records the game, feeds it to LossLocalizer after it ends
LossLocalizer          — Stockfish-based, finds the ply where eval collapsed
SignatureExtractor      — turns that ply + surrounding context into a Signature
SimilarityEngine        — compares new Signatures against existing WeaknessRecords
WeaknessMemory          — persists WeaknessRecords, confidence, decay, effectiveness
PlayerProfile Store     — per-player style vector, strength estimate, record
PatchEngine             — applies WeaknessRecord penalties during MultiPV re-ranking
MoveSelector            — wraps Stockfish + PatchEngine, returns the actual move
StrengthController      — sets skill level / depth based on PlayerProfile + game count
```

## 8. Tech stack

- **python-chess** — board state, PGN parsing, legality
- **Stockfish (UCI)** — both live play (skill level, depth, MultiPV) and post-game analysis
- **FastAPI** — game session + adaptation API, fits existing stack
- **Postgres** (SQLite fine for prototyping) — Signatures, WeaknessRecords, PlayerProfiles
- **scikit-learn**, optional — only if the hand-tuned similarity function in section 2 turns out to need actual learned weights instead of fixed ones
- No LLM in the move-selection path. Chess calculation stays deterministic and strong; an LLM could later narrate adaptation events for the UI ("Mahoraga noticed you favor early queen attacks") but should never touch move choice.

## 9. UI: the adaptation wheel

Eight handles arranged radially, each representing an aggregate confidence score across the WeaknessRecords tagged to that category:

```
Openings · Tactics · King safety · Development · Endgames · Time mgmt · Structure · Psychology
```

Each handle's fill level is the confidence-weighted average of its category's WeaknessRecords, read directly from WeaknessMemory — no separate UI-side calculation. After each game, handles that received a new or reinforced signature visibly fill further and the wheel turns. When the section 0.1 threshold is crossed, the wheel spins to a locked, fully-lit state — the "domain expansion" moment.

Two categories (Time management, Psychology) depend on the behavioral-adaptation layer that's explicitly out of scope for v1 (see section 6 and the earlier scope notes) — they'll sit mostly unfilled until that layer exists, which is fine and honest rather than faking progress there.

## 10. MVP definition

Proves exactly one thing: **a phenomenon experienced once measurably reduces its own future success rate against the same player, without degrading Mahoraga's overall move quality.**

Scope: GameObserver, LossLocalizer, SignatureExtractor, SimilarityEngine, WeaknessMemory (watching/adapted only, no decay tuning yet), PatchEngine (rule-injection tier only), MoveSelector, single hardcoded player profile. No UI polish, no leaderboard, no global mode, no behavioral-layer modeling, no dashboard. Those are all real v2/v3 ideas, but they're worthless if the core loop above doesn't hold up under the offline validation harness first.
