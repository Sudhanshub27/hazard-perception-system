"""
WebSocket Streaming Route — Phase 1 Stub
Full implementation in Phase 5.
"""
import os
import traceback
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from ..pipeline.processor import FrameProcessor

router = APIRouter(prefix="/ws", tags=["stream"])

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def send(self, ws: WebSocket, data: dict):
        try:
            await ws.send_json(data)
        except Exception:
            pass

manager = ConnectionManager()

MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://127.0.0.1:8001")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
if not os.path.exists(UPLOAD_DIR) and not UPLOAD_DIR.startswith("/app"):
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "uploads")
# For local Windows development overrides
if os.name == 'nt' and UPLOAD_DIR == "/app/uploads":
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "uploads")

@router.websocket("/stream/{video_id}")
async def stream_video(websocket: WebSocket, video_id: str):
    await manager.connect(websocket)
    
    video_path = None
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            if f.startswith(video_id):
                video_path = os.path.join(UPLOAD_DIR, f)
                break
            
    if not video_path:
        print(f"[StreamRoute] CRITICAL: Video {video_id} not found in {UPLOAD_DIR}")
        await manager.send(websocket, {"error": "Video not found"})
        manager.disconnect(websocket)
        return

    processor = FrameProcessor(model_service_url=MODEL_SERVICE_URL)
    
    try:
        await manager.send(websocket, {
            "type": "status",
            "message": f"Stream starting for video_id={video_id}..."
        })
        
        async for frame_result in processor.process_video(video_path):
            await manager.send(websocket, {
                "type": "frame",
                "payload": frame_result.model_dump()
            })
            
        await manager.send(websocket, {"type": "end_of_stream"})
        
    except WebSocketDisconnect:
        print(f"Client disconnected from stream {video_id}")
    except Exception as e:
        print(f"[StreamRoute EXCEPTION]: {e}")
        traceback.print_exc()
    finally:
        manager.disconnect(websocket)


