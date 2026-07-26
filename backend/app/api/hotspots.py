"""Router for DBSCAN incident hotspots."""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends

from ..core.security import require_roles
from ..services.analytics.hotspots import hotspot_payload

router = APIRouter(prefix="/api", tags=["hotspots"])


@router.get("/hotspots")
def get_hotspots(user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))) -> Dict[str, Any]:
    """Retrieve spatial crime incident hotspots computed using DBSCAN."""
    return {"items": hotspot_payload(), "data_window_days": 7, "human_review_required": True}
