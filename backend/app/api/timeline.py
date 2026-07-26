"""API Router exposing investigation timeline events for specific criminal cases."""

from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from ..core.security import require_roles
from ..db.repositories import CaseRepository
from ..schemas.responses import TimelineResponse
from ..services.timeline import get_case_timeline

router = APIRouter(prefix="/api", tags=["timeline"])


def get_timeline_service():
    """Dependency provider returning the case timeline compiler service."""
    return get_case_timeline


@router.get("/cases/{case_id}/timeline", response_model=TimelineResponse)
def get_case_timeline_endpoint(
    case_id: str,
    timeline_service = Depends(get_timeline_service),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin")),
) -> TimelineResponse:
    """Retrieve the sorted, source-resolved investigation journey timeline for a case dossier."""
    case = CaseRepository.get_case_profile(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    payload = timeline_service(case_id)
    return TimelineResponse(**payload)
