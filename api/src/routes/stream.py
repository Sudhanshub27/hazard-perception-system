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
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

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
        await ws.send_json(data)


manager = ConnectionManager()


@router.websocket("/stream/{video_id}")
async def stream_video(websocket: WebSocket, video_id: str):
    """
    WebSocket endpoint — streams annotated frames + risk scores.

    Client connects → receives frame results until video ends or client disconnects.

    Phase 5 implementation:
        async for frame_result in processor.process_video(video_path):
            await manager.send(websocket, frame_result.model_dump())
    """
    await manager.connect(websocket)
    try:
        # Stub: send a placeholder message then wait
        await manager.send(websocket, {
            "type": "status",
            "message": f"Connected to stream for video_id={video_id}. Processing pipeline active in Phase 5."
        })
        # Keep connection alive until client disconnects
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
