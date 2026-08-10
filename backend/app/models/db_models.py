from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


def now() -> datetime:
    return datetime.now(timezone.utc)


class Player(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=now)
    estimated_strength: int = 800
    games_played: int = 0
    mahoraga_wins: int = 0
    player_wins: int = 0
    draws: int = 0
    style_vector: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class Game(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    player_id: UUID = Field(foreign_key="player.id", index=True)
    pgn: str = ""
    fen: str = ""
    moves: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    result: str = "*"
    started_at: datetime = Field(default_factory=now)
    ended_at: datetime | None = None


class SignatureRecord(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    player_id: UUID = Field(foreign_key="player.id", index=True)
    game_id: UUID = Field(foreign_key="game.id", index=True)
    phenomenon: str
    motifs: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    phase: str
    features: dict[str, float] = Field(default_factory=dict, sa_column=Column(JSON))
    severity: float
    ply: int
    created_at: datetime = Field(default_factory=now)


class WeaknessRecord(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    player_id: UUID = Field(foreign_key="player.id", index=True)
    phenomenon: str
    motifs: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    phase: str
    representative_features: dict[str, float] = Field(default_factory=dict, sa_column=Column(JSON))
    matched_signature_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    occurrences: int = 1
    confidence: float = 1 / 3
    status: str = "watching"
    last_seen_game_id: UUID | None = Field(default=None, foreign_key="game.id")
    last_seen_at: datetime = Field(default_factory=now)
    opponent_success_before: float | None = None
    opponent_success_after: float | None = None
