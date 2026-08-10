from app.adaptation.confidence import confidence_for, status_for


def test_second_occurrence_adapts() -> None:
    confidence = confidence_for(2)
    assert confidence == 0.5
    assert status_for(2, confidence) == "adapted"


def test_low_confidence_archives() -> None:
    assert status_for(1, 0.24) == "archived"
