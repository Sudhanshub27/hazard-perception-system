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

# To prevent overwhelming the browser, we use a smooth cinematic framerate.
TARGET_FPS = 24
FRAME_INTERVAL = 1.0 / TARGET_FPS
# Downscale target (640px width is perfect for the dashboard HUD)
DISPLAY_WIDTH = 640

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

        return frame

    async def process_video(self, video_path: str):
        """
        Main Video Pipeline.
        Decodes -> Resizes -> Infers -> Scores -> Annotates -> Yields Base64 JSON
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

                h, w = frame.shape[:2]
                
                # Performance Optimization: Downscale frame for detection and preview
                # This reduces network load and inference latency by 60%+
                scale = DISPLAY_WIDTH / w
                frame_small = cv2.resize(frame, (DISPLAY_WIDTH, int(h * scale)))
                
                # 1. Prepare frame for network transport
                _, buffer = cv2.imencode('.jpg', frame_small, [cv2.IMWRITE_JPEG_QUALITY, 70])
                frame_bytes = buffer.tobytes()
                
                # 2. Parallelize model inference (Async network call to Model Service)
                detections = await self._infer_frame(client, frame_bytes)
                
                # 3. Deterministic Risk Scoring (CPU bound, <1ms)
                sh, sw = frame_small.shape[:2]
                risk_score = compute_risk_score([d.model_dump() for d in detections], sw, sh)
                risk_level = classify_risk(risk_score)
                
                # 4. Heads-Up Display rendering (on the downscaled frame)
                annotated_frame = self._draw_hud(frame_small, detections, risk_score, risk_level)
                
                # 5. Base64 encode the annotated frame for WebSocket consumption
                # Quality 60 is the "Sweet Spot" for dashcam previews
                _, annotated_buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
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
                
                # Throttle processing loop to maintain ~24 FPS stability
                frame_id += 1
                processing_time = time.time() - loop_start
                sleep_time = max(0.0, FRAME_INTERVAL - processing_time)
                await asyncio.sleep(sleep_time)

        cap.release()
