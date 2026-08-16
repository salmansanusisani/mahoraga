from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models.db_models import Game, Player, WeaknessRecord
from app.models.schemas import PlayerCreate

router = APIRouter(prefix="/players", tags=["players"])


@router.post("")
def create_player(payload: PlayerCreate, session: Session = Depends(get_session)):
    player = Player(estimated_strength=payload.estimated_strength)
    session.add(player)
    session.commit()
    session.refresh(player)
    return {"player_id": player.id}


def _player(session: Session, player_id: UUID) -> Player:
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(404, "Player not found")
    return player


@router.get("/{player_id}/profile")
def profile(player_id: UUID, session: Session = Depends(get_session)):
    player = _player(session, player_id)
    return {"player_id": player.id, "estimated_strength": player.estimated_strength, "games_played": player.games_played, "record": {"mahoraga_wins": player.mahoraga_wins, "player_wins": player.player_wins, "draws": player.draws}, "style_vector": player.style_vector}


@router.get("/{player_id}/weaknesses")
def weaknesses(player_id: UUID, session: Session = Depends(get_session)):
    _player(session, player_id)
    return session.exec(select(WeaknessRecord).where(WeaknessRecord.player_id == player_id)).all()


@router.get("/{player_id}/wheel")
def wheel(player_id: UUID, session: Session = Depends(get_session)):
    _player(session, player_id)
    records = session.exec(select(WeaknessRecord).where(WeaknessRecord.player_id == player_id, WeaknessRecord.status != "archived")).all()
    handles = {key: 0.0 for key in ("Openings", "Tactics", "King safety", "Development", "Endgames", "Time mgmt", "Structure", "Psychology")}
    counts = {key: 0 for key in handles}
    tactician = {"fork", "pin", "sacrifice"}
    king_risk = {"king_attack", "back_rank"}
    structural = {"positional_decline"}
    for record in records:
        touched: list[str] = []
        if record.phenomenon in tactician:
            touched.append("Tactics")
        if record.phenomenon in king_risk:
            touched.append("King safety")
        if record.phenomenon in structural:
            touched.append("Structure")
        if record.phase == "opening":
            touched.append("Openings")
        elif record.phase == "endgame":
            touched.append("Endgames")
        for handle in touched:
            handles[handle] += record.confidence
            counts[handle] += 1
    return {key: round(handles[key] / counts[key], 3) if counts[key] else 0.0 for key in handles}


@router.get("/{player_id}/adaptation-status")
def adaptation_status(player_id: UUID, session: Session = Depends(get_session)):
    player = _player(session, player_id)
    records = session.exec(select(WeaknessRecord).where(WeaknessRecord.player_id == player_id)).all()
    confirmed = [record for record in records if record.status == "adapted" and record.confidence >= 0.85]
    recent_games = session.exec(select(Game).where(Game.player_id == player_id).order_by(Game.started_at.desc()).limit(10)).all()
    completed = [game for game in recent_games if game.result != "*"]
    win_rate = sum(game.result == "0-1" for game in completed) / len(completed) if completed else 0.0
    effective = [record for record in records if record.opponent_success_before is not None and record.opponent_success_after is not None and record.opponent_success_after < record.opponent_success_before]
    coverage = len(confirmed) / len(records) if records else 0.0
    return {"fully_adapted": bool(records) and coverage >= 0.9 and win_rate >= 0.7 and bool(effective), "adapted_coverage": round(coverage, 3), "trailing_win_rate": round(win_rate, 3), "effective_records": len(effective), "requirements": {"adapted_coverage": 0.9, "trailing_win_rate": 0.7, "effectiveness_required": True}}
