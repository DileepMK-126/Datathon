"""Router for crime incident trends and Isolation Forest anomaly flags."""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query

from ..core.security import require_roles
from ..db.models import ZONE_INDEX
from ..services.analytics.anomaly import trend_payload

router = APIRouter(prefix="/api", tags=["trends"])


@router.get("/trends")
def get_trends(
    zone_id: str | None = Query(default=None),
    days: int = Query(default=28, ge=14, le=60),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin")),
) -> Dict[str, Any]:
    """Retrieve crime incident volume history and Isolation Forest anomalies."""
    if zone_id and zone_id not in ZONE_INDEX:
        raise HTTPException(status_code=404, detail="Unknown zone")
    return trend_payload(zone_id, days)
