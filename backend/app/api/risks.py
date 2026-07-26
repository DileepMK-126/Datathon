"""Router for explainable Random Forest risk forecasts."""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException

from ..core.security import require_roles
from ..services.analytics.risk import risk_payload

router = APIRouter(prefix="/api", tags=["risks"])


@router.get("/risks")
def get_risks(user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))) -> Dict[str, Any]:
    """Retrieve forecast risk scores and explainable drivers for all zones."""
    return {"items": risk_payload(), "human_review_required": True}


@router.get("/risks/{zone_id}")
def get_risk_detail(zone_id: str, user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))) -> Dict[str, Any]:
    """Retrieve detailed risk forecast and drivers for a specific zone."""
    risk = next((item for item in risk_payload() if item["zone_id"] == zone_id), None)
    if not risk:
        raise HTTPException(status_code=404, detail="Unknown zone")
    return risk
