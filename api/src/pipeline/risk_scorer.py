"""
Risk Scoring Module — Phase 1 Skeleton
Full implementation in Phase 4.

This module is deliberately rule-based (NOT a neural network).
WHY?
  - Fully interpretable: you can explain every number in an interview
  - No training data needed for the scorer itself
  - Deterministic: same detections → same score every time
  - Fast: pure Python/NumPy, adds <1ms per frame

Algorithm overview (Phase 4):
  1. Base weight:   each class has a danger weight (pedestrian=10, sign=1)
  2. Proximity:     bbox area / frame area → normalized 0–1
  3. Position:      distance from center-bottom → inverted score
  4. Per-object score: base_weight × proximity × position
  5. Frame score:   sum of all object scores, clipped to [0, 100]
"""
from __future__ import annotations


# Danger weights per BDD100K class (higher = more dangerous)
# Tunable without retraining — just change these values
DANGER_WEIGHTS = {
    "person":        10.0,
    "rider":          8.0,
    "bicycle":        7.0,
    "motorcycle":     7.0,
    "car":            5.0,
    "truck":          6.0,
    "bus":            6.0,
    "traffic light":  3.0,
    "traffic sign":   1.0,
    "train":          9.0,
}

# Risk level thresholds
THRESHOLDS = {
    "safe":     (0,  30),
    "caution":  (31, 60),
    "danger":   (61, 85),
    "critical": (86, 100),
}


def classify_risk(score: float) -> str:
    """Map a 0–100 score to a named risk level."""
    if score <= 30:
        return "safe"
    elif score <= 60:
        return "caution"
    elif score <= 85:
        return "danger"
    else:
        return "critical"


def compute_risk_score(detections: list[dict], frame_w: int, frame_h: int) -> float:
    """
    Compute a frame-level risk score from 0–100.

    Args:
        detections: list of detection dicts from inference.py
        frame_w:    frame width in pixels
        frame_h:    frame height in pixels

    Returns:
        float in [0.0, 100.0]

    Full implementation in Phase 4.
    """
    if not detections:
        return 0.0

    # Placeholder — returns 0 until Phase 4
    return 0.0
