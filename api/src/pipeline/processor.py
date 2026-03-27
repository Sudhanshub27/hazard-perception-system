"""
Video Processing Pipeline — The Engine of the Request
Loops video frames, calls the model service, applies risk scoring, and annotates frames.
"""
from __future__ import annotations
import asyncio
import base64
import os
import time

import cv2
import httpx
import numpy as np

from .risk_scorer import compute_risk_score, classify_risk
from ..models.schemas import FrameResult, Detection

# To prevent overwhelming the model service, we throttle FPS slightly.
TARGET_FPS = 30
FRAME_INTERVAL = 1.0 / TARGET_FPS

class FrameProcessor:
    def __init__(self, model_service_url: str):
        # Default to localhost if running outside Docker
        self.model_service_url = model_service_url or "http://localhost:8001"
        self.infer_url = f"{self.model_service_url}/infer"

    async def _infer_frame(self, client: httpx.AsyncClient, frame_bytes: bytes) -> list[Detection]:
        """Send JPEG payload to the standalone ONNX Model Service."""
        try:
            files = {"file": ("frame.jpg", frame_bytes, "image/jpeg")}
            response = await client.post(self.infer_url, files=files, timeout=2.0)
            
            if response.status_code == 200:
                data = response.json()
                # Parse raw dicts from the model service into our schema
                return [Detection(**d) for d in data.get("detections", [])]
            return []
        except Exception as e:
            print(f"[Processor ERROR] Model inference failed: {e}")
            return []

    def _draw_hud(self, frame: np.ndarray, detections: list[Detection], risk_score: float, risk_level: str) -> np.ndarray:
        """
        Draws the heads-up display (HUD): bounding boxes and risk telemetry.
        """
        # Define color palette based on risk
        colors = {
            "safe":     (0, 255, 0),    # Green
            "caution":  (0, 200, 255),  # Yellow
            "danger":   (0, 0, 255),    # Red
            "critical": (255, 0, 255)   # Magenta
        }
        hud_color = colors.get(risk_level, (255, 255, 255))
        
        # Draw bounding boxes (Red for vehicles/people, Green for signs)
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det.bbox]
            
            # Thick red box for people, thin blue box for cars, etc.
            box_color = (0, 0, 255) if det.class_name in ["person", "rider"] else (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            
            # Draw label background and text
            label = f"{det.class_name} {det.confidence:.1f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), box_color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        # Draw Global Risk Telemetry Dashboard in top-left
        cv2.rectangle(frame, (10, 10), (350, 90), (0, 0, 0), -1)  # Black background HUD
        cv2.putText(frame, f"SYSTEM RISK SCORE: {risk_score}", (20, 40), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, hud_color, 2)
        cv2.putText(frame, f"THREAT LEVEL: {risk_level.upper()}", (20, 75), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, hud_color, 1)

        return frame

    async def process_video(self, video_path: str):
        """
        Main Video Pipeline.
        Decodes -> JPEG encodes -> Infers -> Scores -> Annotates -> Yields Base64 JSON
        """
        if not os.path.exists(video_path):
            print(f"[Processor ERROR] Video file missing: {video_path}")
            return
            
        cap = cv2.VideoCapture(video_path)
        frame_id = 0
        
        # Persistent HTTP client to avoid handshake overhead on every frame
        async with httpx.AsyncClient() as client:
            while cap.isOpened():
                loop_start = time.time()
                
                success, frame = cap.read()
                if not success:
                    break  # End of video
                
                # 1. Prepare frame for network transport
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_bytes = buffer.tobytes()
                
                # 2. Parallelize model inference (Async network call to Model Service)
                detections = await self._infer_frame(client, frame_bytes)
                
                # 3. Deterministic Risk Scoring (CPU bound, <1ms)
                h, w = frame.shape[:2]
                risk_score = compute_risk_score([d.model_dump() for d in detections], w, h)
                risk_level = classify_risk(risk_score)
                
                # 4. Heads-Up Display rendering
                annotated_frame = self._draw_hud(frame, detections, risk_score, risk_level)
                
                # 5. Base64 encode the annotated frame for WebSocket consumption
                _, annotated_buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_b64 = base64.b64encode(annotated_buffer).decode("utf-8")
                
                # 6. Build FrameResult payload
                timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                result = FrameResult(
                    frame_id=frame_id,
                    timestamp_ms=timestamp_ms,
                    detections=detections,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    frame_b64=frame_b64
                )
                
                yield result
                
                # Throttle processing loop to maintain ~30 FPS stability
                frame_id += 1
                processing_time = time.time() - loop_start
                sleep_time = max(0.0, FRAME_INTERVAL - processing_time)
                await asyncio.sleep(sleep_time)

        cap.release()
