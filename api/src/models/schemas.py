"""
Pydantic Schemas — Shared request/response models for the API service.
These define the contract between API and frontend, and between API and model service.
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ============================================================
# Enums
# ============================================================

class RiskLevel(str, Enum):
    SAFE     = "safe"       # 0–30
    CAUTION  = "caution"    # 31–60
    DANGER   = "danger"     # 61–85
    CRITICAL = "critical"   # 86–100


# ============================================================
# Detection — one bounding box from the model service
# ============================================================

class Detection(BaseModel):
    class_id:    int   = Field(..., ge=0, le=9, description="BDD100K class index 0–9")
    class_name:  str   = Field(..., description="Human-readable class name")
    confidence:  float = Field(..., ge=0.0, le=1.0)
    bbox:        list[float] = Field(..., description="[x1, y1, x2, y2] in pixel coords")


# ============================================================
# Frame Result — everything about one processed frame
# ============================================================

class FrameResult(BaseModel):
    frame_id:    int
    timestamp_ms: float = Field(..., description="Milliseconds into the video")
    detections:  list[Detection]
    risk_score:  float  = Field(..., ge=0.0, le=100.0)
    risk_level:  RiskLevel
    frame_b64:   Optional[str] = Field(None, description="Base64-encoded JPEG (WebSocket only)")


# ============================================================
# WebSocket message — streamed to frontend per frame
# ============================================================

class StreamMessage(BaseModel):
    type:       str = "frame"
    payload:    FrameResult


# ============================================================
# Hazard Event — logged when risk_score > 60
# ============================================================

class HazardEvent(BaseModel):
    id:           int
    video_id:     str
    timestamp_ms: float
    risk_score:   float
    risk_level:   RiskLevel
    detections:   list[Detection]
    thumbnail_b64: Optional[str] = None


# ============================================================
# Video Upload Response
# ============================================================

class UploadResponse(BaseModel):
    video_id:  str
    filename:  str
    size_bytes: int
    message:   str = "Video queued for processing"
