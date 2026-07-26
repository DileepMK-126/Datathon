"""Router for unified threat intelligence engine briefs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException

from ..core.security import require_roles
from ..db.models import ZONE_INDEX
from ..schemas.responses import IntelligenceResponse
from ..services.intelligence import generate_zone_intelligence

router = APIRouter(prefix="/api", tags=["intelligence"])


def get_intelligence_service():
    """Dependency provider returning the intelligence generator callable."""
    return generate_zone_intelligence


@router.get("/intelligence", response_model=IntelligenceResponse)
def get_intelligence(
    zone_id: str = Query(...),
    intelligence_service = Depends(get_intelligence_service),
    user: dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin")),
) -> IntelligenceResponse:
    """Retrieve priority-ranked intelligence summary for a specified zone."""
    if zone_id not in ZONE_INDEX:
        raise HTTPException(status_code=404, detail="Unknown zone")
    payload = intelligence_service(zone_id)
    return IntelligenceResponse(**payload)

