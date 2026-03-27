"""
Frame Processing Pipeline — Phase 1 Skeleton
Full implementation in Phase 5.

This module connects:
  OpenCV (video decoding) → Model Service (ONNX inference)
  → Risk Scorer → OpenCV (annotation) → WebSocket (streaming)
"""
from __future__ import annotations
import asyncio


class FrameProcessor:
    """
    Reads frames from a video source, runs the full pipeline,
    and yields annotated FrameResult objects.

    Full implementation in Phase 5:
      - cv2.VideoCapture for file or webcam input
      - httpx async calls to model service /infer
      - risk_scorer.compute_risk_score per frame
      - cv2 bounding box + risk overlay annotation
      - base64 JPEG encoding for WebSocket transport
    """

    def __init__(self, model_service_url: str):
        self.model_service_url = model_service_url

    async def process_video(self, video_path: str):
        """
        Async generator — yields one FrameResult per frame.
        Used by the WebSocket route to stream results.

        Usage (Phase 5):
            async for frame_result in processor.process_video(path):
                await websocket.send_json(frame_result.model_dump())
        """
        # Placeholder
        await asyncio.sleep(0)
        return
        yield  # makes this an async generator (required even for placeholder)
