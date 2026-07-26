"""Router for system access audit records."""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends, Query

from ..core.security import require_roles
from ..db.repositories import AuditRepository

router = APIRouter(prefix="/api", tags=["audit"])


@router.get("/audit")
def get_audit_log(
    limit: int = Query(default=100, ge=1, le=500),
    user: Dict[str, str] = Depends(require_roles("admin")),
) -> Dict[str, Any]:
    """Retrieve application access log history."""
    items = AuditRepository.get_audit_logs(limit)
    return {"items": items, "retention_notice": "Audit retention, SIEM export, and legal hold must be configured by the deploying agency."}
