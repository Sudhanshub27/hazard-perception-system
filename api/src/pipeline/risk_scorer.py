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
        detections: list of detection dicts {"class_name": str, "bbox": [x1, y1, x2, y2]}
        frame_w:    frame width in pixels (e.g., 640)
        frame_h:    frame height in pixels (e.g., 640)

    Returns:
        float in [0.0, 100.0]
    """
    if not detections:
        return 0.0

    frame_area = frame_w * frame_h
    # The bottom-center coordinate of the frame (where the user's car hood is relative to the dashcam)
    car_x = frame_w / 2.0
    car_y = frame_h

    total_score = 0.0

    for det in detections:
        class_name = det.get("class_name", "")
        # Get base weight (default to 1.0 if unknown class)
        base_weight = DANGER_WEIGHTS.get(class_name, 1.0)
        
        # Calculate BBox Area & Proximity
        # ---------------------------------------------
        # A larger box means the object is significantly closer to our car
        [x1, y1, x2, y2] = det["bbox"]
        box_area = (x2 - x1) * (y2 - y1)
        proximity_ratio = box_area / frame_area  # scale of 0 to 1
        
        # If proximity is huge (> 40% of screen), cap the modifier to prevent runaway scores
        proximity_modifier = min(proximity_ratio * 10.0, 4.0)
        
        # Calculate Position Risk (Euclidean Distance)
        # ---------------------------------------------
        # Objects directly in front of the car (bottom-center) are the highest risk.
        # Objects far away in the top corners log lower risk.
        obj_center_x = (x1 + x2) / 2.0
        obj_center_y = (y1 + y2) / 2.0
        
        # Distance formula: sqrt(dx^2 + dy^2)
        dist = ((obj_center_x - car_x)**2 + (obj_center_y - car_y)**2)**0.5
        
        # Max possible distance is from bottom-center to top-corner
        max_dist = ((frame_w / 2.0)**2 + (frame_h)**2)**0.5
        
        # Invert distance so closer = higher score (0 to 1 multiplier)
        # Using squared scaling so objects aggressively lose threat as they move away from the path
        position_modifier = ((max_dist - dist) / max_dist)**2 
        
        # Final Object Score
        # ---------------------------------------------
        # Base threat * How close it is * Is it in our path?
        # A pedestrian (10) taking up 10% screen space (1.0 mod) right in front (1.0 mod) = 10 pts
        # A traffic sign (1) far away (-mod) = 0.1 pts
        object_score = base_weight * (1.0 + proximity_modifier) * position_modifier
        
        total_score += object_score

    # We aggressively scale up the final sum so a single highly-threatening object can trigger "Critical".
    # And we clamp the absolute max to 100.0
    final_score = min(total_score * 3.5, 100.0)
    
    return round(final_score, 1)

