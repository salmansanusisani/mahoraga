ARCHIVE_THRESHOLD = 0.25


def confidence_for(occurrences: int) -> float:
    return occurrences / (occurrences + 2)


def status_for(occurrences: int, confidence: float) -> str:
    if confidence < ARCHIVE_THRESHOLD:
        return "archived"
    return "adapted" if occurrences >= 2 and confidence >= 0.5 else "watching"
