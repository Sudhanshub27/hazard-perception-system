import json
from fastapi import APIRouter, Query, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db, HazardEventModel
from ..models.schemas import RiskLevel

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/")
async def list_events(
    page:       int        = Query(1, ge=1, description="Page number"),
    per_page:   int        = Query(20, ge=1, le=100),
    risk_level: RiskLevel  = Query(None, description="Filter by risk level"),
    video_id:   str        = Query(None, description="Filter by video ID"),
    db: AsyncSession       = Depends(get_db)
):
    """
    Paginated hazard event log.
    Queries persistent SQLite database for frames where risk_score > 60.
    """
    # 1. Base query
    query = select(HazardEventModel)
    
    # 2. Apply filters
    if risk_level:
        query = query.where(HazardEventModel.risk_level == risk_level.value)
    if video_id:
        query = query.where(HazardEventModel.video_id == video_id)
        
    # 3. Calculate total records matching filters
    count_query = select(func.count()).select_from(query.subquery())
    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0
    
    # 4. Paginate and order by ID descending (most recent first)
    query = query.order_by(HazardEventModel.id.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    res = await db.execute(query)
    models = res.scalars().all()
    
    # 5. Deserialize detections JSON and construct response objects
    events_list = []
    for m in models:
        try:
            detections_data = json.loads(m.detections)
        except Exception:
            detections_data = []
            
        events_list.append({
            "id": m.id,
            "video_id": m.video_id,
            "timestamp_ms": m.timestamp_ms,
            "risk_score": m.risk_score,
            "risk_level": m.risk_level,
            "detections": detections_data,
            "thumbnail_b64": m.thumbnail_b64
        })
        
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "events": events_list
    }
