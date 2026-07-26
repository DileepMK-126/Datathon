"""Router for system health checks."""

from __future__ import annotations

from fastapi import APIRouter

from ..core.config import settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Get system health and operational parameters."""
    return {"status": "ok", "data_mode": "synthetic + governed-ingestion-ready schema", "auth_required": str(settings.AUTH_REQUIRED).lower()}
