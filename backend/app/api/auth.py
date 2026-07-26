"""Router for user authentication and session validation."""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends

from ..core.security import current_user, login
from ..schemas.requests import LoginRequest
from ..core.config import settings

router = APIRouter(prefix="/api", tags=["authentication"])


@router.post("/auth/login")
def auth_login(credentials: LoginRequest) -> Dict[str, Any]:
    """Authenticate credentials and return session token."""
    return login(credentials)


@router.get("/auth/me")
def auth_me(user: Dict[str, str] = Depends(current_user)) -> Dict[str, Any]:
    """Get active user session profile info."""
    return {"user": user, "auth_required": settings.AUTH_REQUIRED}
