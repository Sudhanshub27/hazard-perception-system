"""
API Service — FastAPI Entry Point
Phase 1 skeleton: health check only.
WebSocket, upload, and event log routes added in Phase 5.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(
    title="Hazard Perception — API Service",
    description="Orchestration layer: video ingestion, risk scoring, WebSocket streaming",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Tighten to frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()


@app.get("/health", tags=["ops"])
async def health():
    """Health check for Docker Compose and cloud load balancers."""
    return {
        "status": "ok",
        "service": "api",
        "uptime_seconds": round(time.time() - START_TIME, 1),
    }


@app.get("/", tags=["ops"])
async def root():
    return {
        "message": "API service running.",
        "endpoints": {
            "health":   "GET  /health",
            "upload":   "POST /video/upload  (Phase 5)",
            "stream":   "WS   /ws/stream     (Phase 5)",
            "events":   "GET  /events        (Phase 5)",
        }
    }
