"""
Similarity between two Signatures. Phase-gated: signatures from different
game phases are never compared. This is the function the offline harness
exists to validate.
"""
from __future__ import annotations

import math

from app.adaptation.signature_extractor import Signature

MOTIF_WEIGHT = 0.6
FEATURE_WEIGHT = 0.4
SIMILARITY_THRESHOLD = 0.75

FEATURE_KEYS = ["king_safety", "development", "attack_pressure", "material_swing"]
# material_swing has a wider natural range than the 0-1 features, so it
# needs its own normalization when computing distance
FEATURE_RANGES = {
    "king_safety": (0.0, 1.0),
    "development": (0.0, 1.0),
    "attack_pressure": (0.0, 1.0),
    "material_swing": (-10.0, 10.0),
}


def _jaccard(a: list[str], b: list[str]) -> float:
    set_a, set_b = set(a), set(b)
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def _normalized_euclidean(fa: dict, fb: dict) -> float:
    total = 0.0
    for key in FEATURE_KEYS:
        lo, hi = FEATURE_RANGES[key]
        span = hi - lo
        na = (fa.get(key, 0.0) - lo) / span
        nb = (fb.get(key, 0.0) - lo) / span
        total += (na - nb) ** 2
    max_dist = math.sqrt(len(FEATURE_KEYS))
    return math.sqrt(total) / max_dist


def similarity(a: Signature, b: Signature) -> float | None:
    """
    Returns None if the two signatures aren't comparable (different phase).
    Otherwise returns a 0-1 similarity score.
    """
    if a.phase != b.phase:
        return None
    motif_overlap = _jaccard(a.motifs, b.motifs)
    feature_distance = _normalized_euclidean(a.features, b.features)
    return round(MOTIF_WEIGHT * motif_overlap + FEATURE_WEIGHT * (1 - feature_distance), 4)


def is_same_weakness(a: Signature, b: Signature) -> bool:
    sim = similarity(a, b)
    return sim is not None and sim >= SIMILARITY_THRESHOLD
