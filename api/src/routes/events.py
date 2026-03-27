"""
Hazard Events Route — Phase 1 Stub
Full implementation in Phase 5 (after SQLite schema is defined).
"""
from fastapi import APIRouter, Query
from ..models.schemas import RiskLevel

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/")
async def list_events(
    page:       int        = Query(1, ge=1, description="Page number"),
    per_page:   int        = Query(20, ge=1, le=100),
    risk_level: RiskLevel  = Query(None, description="Filter by risk level"),
    video_id:   str        = Query(None, description="Filter by video ID"),
):
    """
    Paginated hazard event log.
    Returns frames where risk_score > 60, ordered by timestamp descending.

    Phase 5: queries SQLite via SQLAlchemy async session.
    """
    return {
        "page": page,
        "per_page": per_page,
        "total": 0,
        "events": [],
        "message": "Event log active in Phase 5 after database setup."
    }
