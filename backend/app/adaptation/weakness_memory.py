from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session, select

from app.adaptation.confidence import confidence_for, status_for
from app.adaptation.signature_extractor import Signature
from app.adaptation.similarity import similarity
from app.models.db_models import SignatureRecord, WeaknessRecord


def _record_signature(session: Session, player_id: UUID, game_id: UUID, signature: Signature) -> SignatureRecord:
    record = SignatureRecord(player_id=player_id, game_id=game_id, **signature.to_dict())
    session.add(record)
    session.flush()
    return record


def _as_signature(record: WeaknessRecord) -> Signature:
    return Signature(record.phenomenon, record.motifs, record.phase, record.representative_features, 0.0, 0)


def update_from_signature(session: Session, player_id: UUID, game_id: UUID, signature: Signature) -> WeaknessRecord:
    signature_record = _record_signature(session, player_id, game_id, signature)
    candidates = session.exec(select(WeaknessRecord).where(WeaknessRecord.player_id == player_id, WeaknessRecord.status != "archived")).all()
    matches = [(similarity(signature, _as_signature(record)) or 0.0, record) for record in candidates]
    score, record = max(matches, default=(0.0, None), key=lambda item: item[0])
    if record is None or score < 0.75:
        record = WeaknessRecord(
            player_id=player_id, phenomenon=signature.phenomenon, motifs=signature.motifs,
            phase=signature.phase, representative_features=signature.features,
            matched_signature_ids=[str(signature_record.id)], last_seen_game_id=game_id,
            opponent_success_before=1.0, opponent_success_after=1.0,
        )
        session.add(record)
        return record
    old_count = record.occurrences
    record.occurrences += 1
    record.confidence = confidence_for(record.occurrences)
    record.status = status_for(record.occurrences, record.confidence)
    record.motifs = sorted(set(record.motifs) | set(signature.motifs))
    record.representative_features = {
        name: (record.representative_features.get(name, 0.0) * old_count + value) / record.occurrences
        for name, value in signature.features.items()
    }
    record.matched_signature_ids = [*record.matched_signature_ids, str(signature_record.id)]
    record.last_seen_game_id = game_id
    record.last_seen_at = datetime.now(timezone.utc)
    session.add(record)
    return record


def refresh_effectiveness(session: Session, player_id: UUID, games_played: int) -> None:
    for record in active_records(session, player_id):
        # Recorded recurrences are the player's success events. As Mahoraga
        # wins future games without recurrence, this measured rate falls.
        record.opponent_success_after = round(record.occurrences / max(1, games_played), 3)
        session.add(record)


def active_records(session: Session, player_id: UUID) -> list[WeaknessRecord]:
    return session.exec(select(WeaknessRecord).where(WeaknessRecord.player_id == player_id, WeaknessRecord.status != "archived")).all()


def decay_unseen(session: Session, player_id: UUID, seen_ids: set[UUID]) -> None:
    for record in active_records(session, player_id):
        if record.id not in seen_ids:
            record.confidence *= 0.95
            record.status = status_for(record.occurrences, record.confidence)
            session.add(record)
