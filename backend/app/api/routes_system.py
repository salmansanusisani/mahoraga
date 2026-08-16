"""
System/admin routes: wiping Mahoraga's memory so it can be tested from a
clean slate. A full reset deletes every row in every table; a per-player
reset clears one player's games, signatures and weaknesses and returns
their stats to the starting defaults.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, delete

from app.db import get_session
from app.models.db_models import Game, Player, SignatureRecord, WeaknessRecord

router = APIRouter(tags=["system"])

# Foreign-key-safe delete order: dependents before their parents.
ALL_TABLES = [SignatureRecord, WeaknessRecord, Game, Player]


@router.post("/admin/reset")
def reset_all(session: Session = Depends(get_session)):
    """Wipe every row in the database - Mahoraga starts with no memory."""
    for table in ALL_TABLES:
        session.exec(delete(table))
    session.commit()
    return {"reset": True, "players_deleted": True, "message": "Mahoraga's memory has been erased."}


@router.delete("/players/{player_id}/memory")
def clear_player_memory(player_id: UUID, session: Session = Depends(get_session)):
    player = session.get(Player, player_id)
    if player is None:
        raise HTTPException(404, "Player not found")
    session.exec(delete(SignatureRecord).where(SignatureRecord.player_id == player_id))
    session.exec(delete(WeaknessRecord).where(WeaknessRecord.player_id == player_id))
    session.exec(delete(Game).where(Game.player_id == player_id))
    player.games_played = 0
    player.estimated_strength = 200
    player.mahoraga_wins = 0
    player.player_wins = 0
    player.draws = 0
    player.style_vector = {}
    session.add(player)
    session.commit()
    return {"reset": True, "player_id": str(player_id), "message": "This player's memory has been erased."}