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
        # Default to localhost if running outside Docker (Enforce IPv4 127.0.0.1 due to Windows pip HTTPX IPv6 localhost bugs)
        self.model_service_url = model_service_url or "http://127.0.0.1:8001"
        self.model_service_url = self.model_service_url.replace("localhost", "127.0.0.1")
        self.infer_url = f"{self.model_service_url}/infer"

    async def _infer_frame(self, client: httpx.AsyncClient, frame_bytes: bytes) -> list[Detection]:
        """Send JPEG payload to the standalone YOLO Model Service.
        Note: client must be created with trust_env=False to bypass system proxies."""
        try:
            files = {"file": ("frame.jpg", frame_bytes, "image/jpeg")}
            # 15s timeout to allow for model load if it's currently starting up
            response = await client.post(self.infer_url, files=files, timeout=15.0)
            
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    print(f"[Processor] Model Service returned internal error: {data['error']}")
                    return []
                return [Detection(**d) for d in data.get("detections", [])]
            elif response.status_code == 503:
                # 503 usually means the model's startup event isn't finished yet
                print(f"[Processor] Model Service is still booting (503). Skipping frame...")
                return []
            else:
                print(f"[Processor ERROR] Model Service status {response.status_code}")
                return []
        except httpx.ConnectError:
            print(f"[Processor ERROR] Could not reach Model Service at {self.infer_url}. Is it running?")
            return []
        except Exception as e:
            print(f"[Processor ERROR] Unexpected inference fail: {repr(e)}")
            return []

    @staticmethod
    def _draw_hud(frame: np.ndarray, detections: list[Detection], risk_score: float, risk_level: str) -> np.ndarray:
        """
        Draws the heads-up display (HUD): bounding boxes and risk telemetry.
        """
        colors = {
            "safe":     (0, 255, 0),    # Green
            "caution":  (0, 200, 255),  # Yellow
            "danger":   (0, 0, 255),    # Red
            "critical": (255, 0, 255)   # Magenta
        }
        hud_color = colors.get(risk_level, (255, 255, 255))
        
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det.bbox]
            
            box_color = (0, 0, 255) if det.class_name in ["person", "rider"] else (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            
            label = f"{det.class_name} {det.confidence:.1f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            cv2.rectangle(frame, (x1, y1 - 15), (x1 + w, y1), box_color, -1)
            cv2.putText(frame, label, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)

        return frame

    def _sync_read_and_prepare(self, cap: cv2.VideoCapture) -> tuple[bool, bytes | None, np.ndarray | None, int, int]:
        """Synchronous CPU-bound wrapper for reading and scaling the frame.
        Always outputs a 16:9 frame (640x360) regardless of source resolution.
        """
        success, frame = cap.read()
        if not success:
            return False, None, None, 0, 0

        h, w = frame.shape[:2]
        target_ratio = 16.0 / 9.0
        current_ratio = w / h

        # Center-crop to 16:9 if the source aspect ratio doesn't match
        if abs(current_ratio - target_ratio) > 0.05:
            if current_ratio > target_ratio:
                # Too wide — crop sides
                new_w = int(h * target_ratio)
                x_off = (w - new_w) // 2
                frame = frame[:, x_off:x_off + new_w]
            else:
                # Too tall — crop top/bottom (center crop keeps road in view)
                new_h = int(w / target_ratio)
                y_off = (h - new_h) // 2
                frame = frame[y_off:y_off + new_h, :]

        # Now resize to consistent display size (640 wide, 360 tall = 16:9)
        sw, sh = DISPLAY_WIDTH, int(DISPLAY_WIDTH / target_ratio)
        frame_small = cv2.resize(frame, (sw, sh))
        
        # 1. Prepare frame for network transport
        _, buffer = cv2.imencode('.jpg', frame_small, [cv2.IMWRITE_JPEG_QUALITY, 75])
        return True, buffer.tobytes(), frame_small, sw, sh

    def _sync_annotate_and_encode(self, frame_small: np.ndarray, detections: list[Detection], risk_score: float, risk_level: str) -> str:
        """Synchronous CPU-bound wrapper for drawing the HUD and compressing to base64."""
        annotated_frame = self._draw_hud(frame_small, detections, risk_score, risk_level)
        _, annotated_buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        return base64.b64encode(annotated_buffer).decode("utf-8")

    async def process_video(self, video_path: str):
        """
        Main Video Pipeline.
        Decodes -> Resizes -> Infers -> Scores -> Annotates -> Yields Base64 JSON
        Runs blocking operations safely wrapped in asyncio threads to protect WebSocket streams.
        """
        if not os.path.exists(video_path):
            print(f"[Processor ERROR] Video file missing: {video_path}")
            return
            
        cap = cv2.VideoCapture(video_path)
        frame_id = 0
        
        async with httpx.AsyncClient(trust_env=False) as client:
            while cap.isOpened():
                loop_start = time.time()
                
                # Safe async offload of heavy I/O and cv2 array math
                success, frame_bytes, frame_small, sw, sh = await asyncio.to_thread(self._sync_read_and_prepare, cap)
                
                if not success or frame_bytes is None or frame_small is None:
                    break
                
                # 2. Parallelize model inference (Async network call to Model Service)
                detections = await self._infer_frame(client, frame_bytes)
                
                # 3. Deterministic Risk Scoring
                risk_score = compute_risk_score([d.model_dump() for d in detections], sw, sh)
                risk_level = classify_risk(risk_score)
                
                # 4 & 5. HUD rendering and Base64 compression
                frame_b64 = await asyncio.to_thread(self._sync_annotate_and_encode, frame_small, detections, risk_score, risk_level)
                
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
                
                frame_id += 1
                processing_time = time.time() - loop_start
                sleep_time = max(0.0, FRAME_INTERVAL - processing_time)
                await asyncio.sleep(sleep_time)

        cap.release()
