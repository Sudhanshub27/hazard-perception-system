"""
Video Upload Route — Phase 1 Stub
Full implementation in Phase 5.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..models.schemas import UploadResponse
import uuid, os

router = APIRouter(prefix="/video", tags=["video"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")


@router.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Accept a dashcam video file and save it for processing.
    Supported formats: .mp4, .avi, .mov, .mkv

    Phase 5: triggers background processing task after saving.
    """
    allowed_types = {"video/mp4", "video/avi", "video/quicktime", "video/x-matroska"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    video_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{video_id}_{file.filename}")

    contents = await file.read()
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(contents)

    return UploadResponse(
        video_id=video_id,
        filename=file.filename,
        size_bytes=len(contents),
    )
