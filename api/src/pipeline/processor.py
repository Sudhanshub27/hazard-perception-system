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

from .risk_scorer import compute_risk_score, classify_risk, get_action_recommendation
from ..models.schemas import FrameResult, Detection

# To prevent overwhelming the browser, we use a smooth cinematic framerate.
TARGET_FPS = 24
FRAME_INTERVAL = 1.0 / TARGET_FPS
# Display resolution — match YOLO's native square input for sharpest detections
DISPLAY_WIDTH = 720   # wider display with more pixels = crisper text
INFER_SIZE = 640      # square crop sent to model for accurate YOLOv8 inference

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
        Uses anti-aliased text and high-quality label backgrounds for crisp readability.
        """
        colors = {
            "safe":     (34,  197, 94),    # Emerald green
            "caution":  (251, 191,  36),   # Amber
            "danger":   (239,  68,  68),   # Red
            "critical": (217,  70, 239)    # Fuchsia
        }
        hud_color = colors.get(risk_level, (255, 255, 255))

        FONT      = cv2.FONT_HERSHEY_DUPLEX   # sharper than SIMPLEX at small sizes
        FONT_SCALE = 0.55                     # larger → less compression blur
        THICKNESS  = 1
        PAD        = 4                        # label background padding in pixels

        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det.bbox]

            # Choose box color: red for people/riders, blue for vehicles
            box_color = (239, 68, 68) if det.class_name in ["person", "rider"] else (59, 130, 246)

            # Draw bounding box — 2px with anti-aliased line cap
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2, cv2.LINE_AA)

            # Build label string with confidence shown as percentage
            label = f"{det.class_name}  {det.confidence * 100:.0f}%"
            (tw, th), baseline = cv2.getTextSize(label, FONT, FONT_SCALE, THICKNESS)

            # Background rectangle with padding so letters aren't clipped
            bg_y1 = max(0, y1 - th - 2 * PAD)
            bg_y2 = y1
            bg_x2 = min(frame.shape[1], x1 + tw + 2 * PAD)

            # Semi-opaque filled background (solid color for JPEG compatibility)
            cv2.rectangle(frame, (x1, bg_y1), (bg_x2, bg_y2), box_color, cv2.FILLED)

            # Crisp white text with LINE_AA anti-aliasing
            text_y = bg_y2 - PAD
            cv2.putText(
                frame, label,
                (x1 + PAD, text_y),
                FONT, FONT_SCALE, (255, 255, 255), THICKNESS, cv2.LINE_AA
            )

        return frame

    def _sync_read_and_prepare(self, cap: cv2.VideoCapture) -> tuple[bool, bytes | None, np.ndarray | None, int, int]:
        """Synchronous CPU-bound wrapper for reading and scaling the frame.
        
        Strategy:
          - Display frame: 16:9 at DISPLAY_WIDTH for the browser canvas (crisp HUD rendering)
          - Infer frame:   square 640x640 center-crop sent to YOLOv8 (matches its native input)
            Sending a square matches YOLO's training image shape → better recall on small objects.
        """
        success, frame = cap.read()
        if not success:
            return False, None, None, 0, 0

        h, w = frame.shape[:2]
        target_ratio = 16.0 / 9.0
        current_ratio = w / h

        # --- Display frame: center-crop to 16:9 ---
        display_frame = frame.copy()
        if abs(current_ratio - target_ratio) > 0.05:
            if current_ratio > target_ratio:
                new_w = int(h * target_ratio)
                x_off = (w - new_w) // 2
                display_frame = display_frame[:, x_off:x_off + new_w]
            else:
                new_h = int(w / target_ratio)
                y_off = (h - new_h) // 2
                display_frame = display_frame[y_off:y_off + new_h, :]

        sw = DISPLAY_WIDTH
        sh = int(DISPLAY_WIDTH / target_ratio)
        frame_display = cv2.resize(display_frame, (sw, sh), interpolation=cv2.INTER_AREA)

        # --- Infer frame: square center-crop for accurate YOLO inference ---
        # Take the central 640x640 square from the full resolution frame.
        # This avoids letterboxing distortion that hurts small-object detection.
        sq = min(h, w, INFER_SIZE)
        cx, cy = w // 2, h // 2
        x0, y0 = cx - sq // 2, cy - sq // 2
        infer_crop = frame[y0:y0 + sq, x0:x0 + sq]
        infer_resized = cv2.resize(infer_crop, (INFER_SIZE, INFER_SIZE), interpolation=cv2.INTER_AREA)

        # Encode infer frame at high quality (85) — better feature preservation for model
        _, buffer = cv2.imencode('.jpg', infer_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return True, buffer.tobytes(), frame_display, sw, sh

    def _sync_annotate_and_encode(self, frame_small: np.ndarray, detections: list[Detection], risk_score: float, risk_level: str) -> str:
        """Synchronous CPU-bound wrapper for drawing the HUD and compressing to base64.
        
        Quality raised to 92: JPEG at 60 creates block artifacts around small text.
        At 92 the text labels stay crisp with only ~30% larger payload.
        """
        annotated_frame = self._draw_hud(frame_small, detections, risk_score, risk_level)
        _, annotated_buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
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
                
                # 3. Deterministic Risk Scoring + Action Recommendation
                det_dicts = [d.model_dump() for d in detections]
                risk_score = compute_risk_score(det_dicts, sw, sh)
                risk_level = classify_risk(risk_score)
                recommendation = get_action_recommendation(det_dicts, risk_score)
                
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
                    recommendation=recommendation,
                    frame_b64=frame_b64
                )
                
                yield result
                
                frame_id += 1
                processing_time = time.time() - loop_start
                sleep_time = max(0.0, FRAME_INTERVAL - processing_time)
                await asyncio.sleep(sleep_time)

        cap.release()
