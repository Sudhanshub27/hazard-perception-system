"""
WebSocket Streaming Route — Phase 1 Stub
Full implementation in Phase 5.

WHY WebSockets over HTTP polling?
  - Polling: client sends request every N ms, most responses are empty
  - WebSocket: server pushes data the instant a frame is ready
  - At 30 FPS: polling would mean 30 HTTP round-trips/sec per client
    WebSocket: 1 persistent connection, ~2ms latency per frame
  - Bi-directional: client can send control messages (pause, stop)
"""
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from ..pipeline.processor import FrameProcessor

router = APIRouter(prefix="/ws", tags=["stream"])

class ConnectionManager:
    """Tracks all active WebSocket clients for broadcast support."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def send(self, ws: WebSocket, data: dict):
        # Make sure not to send to closed sockets
        try:
            await ws.send_json(data)
        except Exception:
            pass

manager = ConnectionManager()

# Default to the Docker composed service URL
MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://localhost:8001")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")

@router.websocket("/stream/{video_id}")
async def stream_video(websocket: WebSocket, video_id: str):
    """
    WebSocket endpoint — streams annotated frames + risk scores.
    """
    await manager.connect(websocket)
    
    # 1. Resolve path to uploaded video
    # In a real app we'd look this up in the DB
    video_path = None
    for f in os.listdir(UPLOAD_DIR):
        if f.startswith(video_id):
            video_path = os.path.join(UPLOAD_DIR, f)
            break
            
    if not video_path:
        await manager.send(websocket, {"error": "Video not found"})
        manager.disconnect(websocket)
        return

    processor = FrameProcessor(model_service_url=MODEL_SERVICE_URL)
    
    try:
        # Acknowledge connection
        await manager.send(websocket, {
            "type": "status",
            "message": f"Stream starting for video_id={video_id}..."
        })
        
        # 2. Main processing loop
        async for frame_result in processor.process_video(video_path):
            # Send the complete frame state (JSON + Base64 image) down the socket
            await manager.send(websocket, {
                "type": "frame",
                "payload": frame_result.model_dump()
            })
            
        # Send end signal
        await manager.send(websocket, {"type": "end_of_stream"})
        
    except WebSocketDisconnect:
        print(f"Client disconnected from stream {video_id}")
    finally:
        manager.disconnect(websocket)

