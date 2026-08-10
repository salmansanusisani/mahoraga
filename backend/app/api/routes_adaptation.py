"""Adaptation event feed: what the learning layer has noticed, in order."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models.db_models import Player, SignatureRecord, WeaknessRecord

router = APIRouter(prefix="/adaptation", tags=["adaptation"])


def _player(session: Session, player_id: UUID) -> Player:
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(404, "Player not found")
    return player


@router.get("/events")
def events(player_id: UUID, limit: int = 20, session: Session = Depends(get_session)):
    """Recent learning events, newest first. Each signature becomes one event
    tagged with the WeaknessRecord it matched into (or 'signature' if none)."""
    _player(session, player_id)
    limit = max(1, min(100, limit))
    signatures = session.exec(
        select(SignatureRecord)
        .where(SignatureRecord.player_id == player_id)
        .order_by(SignatureRecord.created_at.desc())
        .limit(limit)
    ).all()
    records = session.exec(select(WeaknessRecord).where(WeaknessRecord.player_id == player_id)).all()
    record_by_signature = {
        signature_id: record
        for record in records
        for signature_id in record.matched_signature_ids
    }
    events = []
    for signature in signatures:
        record = record_by_signature.get(str(signature.id))
        events.append(
            {
                "type": "signature" if record is None else f"weakness_{record.status}",
                "phenomenon": signature.phenomenon,
                "motifs": signature.motifs,
                "phase": signature.phase,
                "severity": signature.severity,
                "ply": signature.ply,
                "created_at": signature.created_at.isoformat(),
                "status": record.status if record else None,
                "confidence": record.confidence if record else None,
            }
        )
    return {
        "player_id": player_id,
        "events": events,
        "weakness_records": [
            {
                "id": str(record.id),
                "phenomenon": record.phenomenon,
                "motifs": record.motifs,
                "phase": record.phase,
                "occurrences": record.occurrences,
                "confidence": record.confidence,
                "status": record.status,
            }
            for record in records
        ],
    }
