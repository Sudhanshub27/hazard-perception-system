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
    Calculates deterministic collision risk using spatial overlap and class threat level.
    """
    if not detections:
        return 0.0

    frame_area = frame_w * frame_h
    # The car is at the bottom center of the camera FOV
    car_x = frame_w / 2.0
    car_y = frame_h

    total_score = 0.0

    for det in detections:
        class_name = det.get("class_name", "")
        # Get base weight (default to 1.0 if unknown class)
        base_weight = DANGER_WEIGHTS.get(class_name, 1.0)
        
        # Calculate BBox Area & Proximity
        # ---------------------------------------------
        # A larger box means the object is closer to the dashcam
        [x1, y1, x2, y2] = det["bbox"]
        box_area = (max(0, x2 - x1)) * (max(0, y2 - y1))
        proximity_ratio = box_area / frame_area
        
        # Proximity modifier limits runaway but heavily penalizes anything eating >15% field of view.
        # Logarithmic-like scaling using root for smooth rapid approach warning
        proximity_modifier = min((proximity_ratio**0.5) * 8.0, 5.0) 
        
        # Calculate Position Risk (Euclidean Distance & Trajectory Overlap)
        # ---------------------------------------------
        obj_center_x = (x1 + x2) / 2.0
        obj_bottom_y = y2 # Use the bottom of the bounding box as the physical contact point
        
        dist = ((obj_center_x - car_x)**2 + (obj_bottom_y - car_y)**2)**0.5
        max_dist = ((frame_w / 2.0)**2 + (frame_h)**2)**0.5
        
        # Invert distance: 1.0 = right in front, 0.0 = top corner
        position_modifier = ((max_dist - dist) / max_dist)**2 

        # Trajectory multiplier: If the object's x-center is within the middle 30% of the screen, multiply the threat.
        x_center_ratio = abs(obj_center_x - car_x) / frame_w
        trajectory_mult = 1.8 if x_center_ratio < 0.15 else 1.0
        
        # Final Object Score
        object_score = base_weight * (1.0 + proximity_modifier) * position_modifier * trajectory_mult
        
        total_score += object_score

    # Compute bounding saturation curve to naturally clamp the total to 100.0 without a hard plateau
    # Using a soft asymptotic approach: max - max * e^(-x)
    max_cap = 100.0
    # The coefficient `0.04` maps a raw total of ~40 to produce a ~80 (Critical) score.
    normalized_score = max_cap * (1.0 - __import__('math').exp(-0.04 * total_score))
    
    return min(round(normalized_score, 1), 100.0)

