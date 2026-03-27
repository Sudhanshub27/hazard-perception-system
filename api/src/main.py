"""
Orchestrator API Service — Entry Point
Mounts the HTTP and WebSocket routes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import video, stream, events

app = FastAPI(
    title="Hazard Perception — API Service",
    description="Orchestrator backend handling video uploads, WS streams, and risk logic.",
    version="0.1.0",
)

# Crucial for Next.js to communicate across ports!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register individual sub-routers
app.include_router(video.router)
app.include_router(stream.router)
app.include_router(events.router)

@app.get("/health", tags=["ops"])
async def health():
    return {"status": "ok", "service": "api"}
