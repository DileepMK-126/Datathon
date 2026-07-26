"""Router for the daily Executive Morning Intelligence Brief."""

from __future__ import annotations

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from ..core.security import require_roles
from ..schemas.brief import MorningBriefResponse
from ..services.brief.engine import get_morning_brief

router = APIRouter(prefix="/api/intelligence", tags=["brief"])


@router.get("/brief", response_model=MorningBriefResponse)
def get_morning_command_brief(
    date: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Retrieve the daily executive morning brief summary and critical alerts."""
    brief = get_morning_brief(date_str=date, district=district)
    return brief


@router.get("/brief/export", response_class=Response)
def export_morning_brief_file(
    format: str = Query("markdown", regex="^(json|markdown)$"),
    user: Dict[str, str] = Depends(require_roles("supervisor", "admin"))
) -> Response:
    """Export the daily command briefing report (requires supervisor or admin role)."""
    brief = get_morning_brief()
    
    if format == "json":
        import json
        return Response(
            content=json.dumps(brief, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment;filename=morning-brief.json"}
        )
    elif format == "markdown":
        return Response(
            content=brief["markdown"],
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment;filename=morning-brief.md"}
        )
        
    raise HTTPException(status_code=400, detail="Invalid export format requested.")
