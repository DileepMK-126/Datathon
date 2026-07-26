"""Router for NetworkX shared-entity criminal networks."""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends, Query

from ..core.security import require_roles
from ..services.analytics.network import graph_payload

router = APIRouter(prefix="/api", tags=["networks"])


@router.get("/networks")
def get_networks(
    case_id: str | None = Query(default=None),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin")),
) -> Dict[str, Any]:
    """Retrieve criminal association networks linked via shared masked identifiers."""
    return graph_payload(case_id)
