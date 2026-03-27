"""
Model Service — FastAPI Entry Point
Provides a REST endpoint for the Orchestrator API to offload GPU inference.
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import time
import cv2
import numpy as np
import os
from .inference import YOLOInference

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

# 1. Initialize our ONNX inference wrapper globally
WEIGHTS_PATH = os.getenv("MODEL_PATH", "/app/weights/best.onnx")
# For local Windows development without Docker, fallback to relative path
if not os.path.exists(WEIGHTS_PATH):
    WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "..", "weights", "best.onnx")

model = YOLOInference(WEIGHTS_PATH)

@app.on_event("startup")
async def startup_event():
    """Load model graph into memory when server starts."""
    model.load()

@app.get("/health", tags=["ops"])
async def health():
    return {
        "status": "ok",
        "service": "model",
        "model_loaded": model.is_loaded,
        "uptime_seconds": round(time.time() - START_TIME, 1),
    }

@app.post("/infer", tags=["inference"])
async def infer_frame(file: UploadFile = File(...)):
    """
    Accepts an encoded JPEG frame and returns JSON object detections.
    Called hundreds of times per second by the API stream processor.
    """
    if not model.is_loaded:
        return {"error": "Model not loaded. File best.onnx might be missing."}
        
    contents = await file.read()
    
    # Decode raw bytes into an OpenCV Numpy array
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        return {"error": "Failed to decode image"}
        
    # Run YOLO26 Inference
    detections = model.infer(frame)
    
    return {"detections": detections}
