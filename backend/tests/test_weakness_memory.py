from sqlmodel import SQLModel, Session, create_engine, select

from app.adaptation.signature_extractor import Signature
from app.adaptation.weakness_memory import update_from_signature
from app.models.db_models import Game, Player, WeaknessRecord

BASE = {"king_safety": 0.5, "development": 0.5, "attack_pressure": 0.5, "material_swing": 0.0}
EDGE = {"king_safety": 1.0, "development": 1.0, "attack_pressure": 1.0, "material_swing": 10.0}


def _fixture() -> Session:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    player = Player()
    game = Game(player_id=player.id)
    session.add(player)
    session.add(game)
    session.commit()
    return session


def test_borderline_similarity_does_not_merge() -> None:
    session = _fixture()
    player = session.exec(select(Player)).first()
    game = session.exec(select(Game)).first()
    session.add(
        WeaknessRecord(
            player_id=player.id,
            phenomenon="fork",
            motifs=["fork", "pin"],
            phase="opening",
            representative_features=BASE,
            confidence=1 / 3,
        )
    )
    session.commit()

    # 1/2 motif overlap + max feature distance -> similarity 0.5, in the
    # review band [0.5, 0.75): logged for review, never auto-merged.
    update_from_signature(
        session,
        player.id,
        game.id,
        Signature("fork", ["fork"], "opening", EDGE, 0.0, 0),
    )
    records = session.exec(select(WeaknessRecord)).all()
    assert len(records) == 2
    assert all(record.occurrences == 1 for record in records)


def test_strong_similarity_merges() -> None:
    session = _fixture()
    player = session.exec(select(Player)).first()
    game = session.exec(select(Game)).first()
    session.add(
        WeaknessRecord(
            player_id=player.id,
            phenomenon="fork",
            motifs=["fork", "pin"],
            phase="opening",
            representative_features=BASE,
            confidence=1 / 3,
        )
    )
    session.commit()

    # Same motifs, identical features -> similarity 1.0, a real recurrence.
    update_from_signature(
        session,
        player.id,
        game.id,
        Signature("fork", ["fork", "pin"], "opening", dict(BASE), 0.0, 0),
    )
    records = session.exec(select(WeaknessRecord)).all()
    assert len(records) == 1
    assert records[0].occurrences == 2
