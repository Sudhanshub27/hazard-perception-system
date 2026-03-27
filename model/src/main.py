"""
Model Service — FastAPI Entry Point
Phase 1 skeleton: health check only.
Inference routes added in Phase 5.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(
    title="Hazard Perception — Model Service",
    description="YOLO26 ONNX inference endpoint",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()


@app.get("/health", tags=["ops"])
async def health():
    """Used by Docker Compose depends_on and load balancers."""
    return {
        "status": "ok",
        "service": "model",
        "uptime_seconds": round(time.time() - START_TIME, 1),
    }


@app.get("/", tags=["ops"])
async def root():
    return {"message": "Model service running. POST /infer to detect objects (Phase 5)."}
