"""Router for geospatial query endpoints."""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends, Query

from ..core.security import require_roles
from ..db.repositories import IncidentRepository

router = APIRouter(prefix="/api", tags=["geospatial"])


@router.get("/geospatial/incidents")
def geospatial_incidents(
    min_lng: float = Query(...), min_lat: float = Query(...), max_lng: float = Query(...), max_lat: float = Query(...),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin")),
) -> Dict[str, Any]:
    """Retrieve incidents within bounded box using PostGIS or bounding calculations."""
    items = IncidentRepository.get_geospatial_incidents(min_lng, min_lat, max_lng, max_lat)
    return {"items": items, "limit": 500, "human_review_required": True}
