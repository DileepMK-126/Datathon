"""Router for unified case profiles and entity-resolution repeat offender lists."""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends

from ..core.security import require_roles
from ..db.repositories import CaseRepository
from ..services.analytics.network import unified_case_profile
from ..utils.masking import mask_value

router = APIRouter(prefix="/api", tags=["cases"])


@router.get("/cases/{case_id}")
def get_case_profile(case_id: str, user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))) -> Dict[str, Any]:
    """Retrieve details of a single unified case profile, including masked entities and sources."""
    return unified_case_profile(case_id)


@router.get("/repeat-offenders")
def get_repeat_offenders(user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))) -> Dict[str, Any]:
    """Retrieve repeat person entities linked to multiple case records."""
    rows = CaseRepository.get_repeat_offender_persons()
    return {
        "items": [{"label": mask_value(row["display_value"], "person"), "linked_case_count": row["case_count"], "review_required": True} for row in rows],
        "notice": "Matches are entity-resolution leads; analysts must validate identity before any action.",
    }
