from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field


class PlayerCreate(BaseModel):
    estimated_strength: int = Field(default=200, ge=50, le=3000)


class GameCreate(BaseModel):
    player_id: UUID
    skill_level: int | None = Field(default=None, ge=0, le=20)


class MoveRequest(BaseModel):
    move: str


class GameResponse(BaseModel):
    game_id: UUID
    fen: str
    moves: list[str]
    result: str
    mahoraga_move: str | None = None
    message: str | None = None
