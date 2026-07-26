"""Router for external gateways integration adapter endpoints."""

from __future__ import annotations

from typing import Any, Dict
import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from ..core.security import require_roles
from ..integrations.icjs import ICJSConfigurationError, configuration_status, sync_cases

router = APIRouter(prefix="/api", tags=["integrations"])


@router.get("/integrations/icjs/status")
def get_icjs_status(user: Dict[str, str] = Depends(require_roles("admin"))) -> Dict[str, Any]:
    """Retrieve governed ICJS gateway adapter connection status and settings."""
    return configuration_status()


@router.post("/integrations/icjs/sync")
def trigger_icjs_sync(user: Dict[str, str] = Depends(require_roles("admin"))) -> Dict[str, Any]:
    """Trigger a secure compliance case records sync run from ICJS registry."""
    try:
        return sync_cases()
    except ICJSConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="ICJS gateway request failed") from exc
