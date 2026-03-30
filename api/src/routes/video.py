"""
Video Upload Endpoint
Receives MP4/AVI videos from the UI and caches them on disk for processing.
"""
from fastapi import APIRouter, UploadFile, File
import os
import aiofiles
import uuid

router = APIRouter(prefix="/video", tags=["upload"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
if not os.path.exists(UPLOAD_DIR) and not UPLOAD_DIR.startswith("/app"):
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "uploads")
# For local Windows development overrides
if os.name == 'nt' and UPLOAD_DIR == "/app/uploads":
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Saves the incoming video and returns a unique ID.
    The frontend will use this ID to connect the WebSocket stream.
    """
    if not file.filename.lower().endswith(('.mp4', '.avi', '.move')):
        return {"error": "Unsupported file type. Use MP4 or AVI."}
        
    # Generate unique ID to prevent collisions
    video_id = str(uuid.uuid4())[:8]
    extension = file.filename.split('.')[-1]
    safe_filename = f"{video_id}.{extension}"
    
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Save file asynchronously
    async with aiofiles.open(file_path, 'wb') as out_file:
        while content := await file.read(1024 * 1024):  # Read in 1MB chunks
            await out_file.write(content)
            
    return {"status": "success", "video_id": video_id, "filename": file.filename}
