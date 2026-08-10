from app.adaptation.signature_extractor import Signature
from app.adaptation.similarity import is_same_weakness, similarity

BASE = {"king_safety": 0.5, "development": 0.5, "attack_pressure": 0.5, "material_swing": 0.0}


def _sig(motifs: list[str], features: dict, phase: str = "opening") -> Signature:
    return Signature(phenomenon=motifs[0] if motifs else "none", motifs=motifs, phase=phase, features=features)


def test_identical_signatures_score_1() -> None:
    sig = _sig(["fork"], BASE)
    assert similarity(sig, sig) == 1.0


def test_same_weakness_over_threshold() -> None:
    a = _sig(["fork", "pin"], BASE)
    b = _sig(["pin", "fork"], {**BASE, "development": 0.6, "attack_pressure": 0.55})
    assert similarity(a, b) >= 0.75
    assert is_same_weakness(a, b)


def test_different_phases_are_incomparable() -> None:
    assert similarity(_sig(["fork"], BASE, "opening"), _sig(["fork"], BASE, "endgame")) is None
    assert not is_same_weakness(_sig(["fork"], BASE, "opening"), _sig(["fork"], BASE, "endgame"))


def test_disjoint_motifs_score_low() -> None:
    a = _sig(["fork"], BASE)
    b = _sig(["back_rank"], BASE)
    assert similarity(a, b) < 0.5
    assert not is_same_weakness(a, b)


def test_empty_motif_sets_match() -> None:
    assert similarity(_sig([], BASE), _sig([], BASE)) == 1.0
