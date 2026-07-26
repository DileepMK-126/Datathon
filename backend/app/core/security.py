"""Authentication, role checks, and append-only application audit events."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from fastapi import Header, HTTPException, Request, status

from .config import settings
from ..db.connection import connection
from ..schemas.requests import LoginRequest

from functools import lru_cache

ROLE_ORDER = {"analyst": 1, "supervisor": 2, "admin": 3}
PBKDF2_ITERATIONS = 600_000


def utc_now() -> str:
    """Get current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with a secure salt."""
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return "$".join((str(PBKDF2_ITERATIONS), base64.urlsafe_b64encode(salt).decode(), base64.urlsafe_b64encode(derived).decode()))


def verify_password(password: str, stored: str) -> bool:
    """Verify a password against its PBKDF2 stored hash."""
    try:
        iterations, encoded_salt, encoded_hash = stored.split("$", 2)
        expected = base64.urlsafe_b64decode(encoded_hash.encode())
        derived = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.urlsafe_b64decode(encoded_salt.encode()), int(iterations))
        return hmac.compare_digest(derived, expected)
    except (ValueError, TypeError):
        return False


def ensure_bootstrap_user(conn: Any) -> None:
    """Create only an explicitly configured bootstrap administrator if authentication is required."""
    if not settings.AUTH_REQUIRED:
        return
    password = settings.BOOTSTRAP_ADMIN_PASSWORD
    username = settings.BOOTSTRAP_ADMIN_USERNAME
    if not password:
        raise RuntimeError("BOOTSTRAP_ADMIN_PASSWORD must be set before enabling AUTH_REQUIRED")
    existing = conn.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        return
    conn.execute(
        "INSERT INTO users(username, password_hash, role, active, created_at) VALUES (?, ?, ?, ?, ?)",
        (username, hash_password(password), "admin", True, utc_now()),
    )


def issue_token(user: Dict[str, Any]) -> str:
    """Issue a new JWT access token for a user session."""
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_TTL_MINUTES)
    return jwt.encode({"sub": user["username"], "role": user["role"], "exp": expires, "iat": datetime.now(timezone.utc)}, settings.jwt_secret, algorithm="HS256")


def login(credentials: LoginRequest) -> Dict[str, Any]:
    """Verify user credentials and return an access token."""
    with connection() as conn:
        user = conn.execute("SELECT username, password_hash, role, active FROM users WHERE username = ?", (credentials.username,)).fetchone()
    if not user or not user["active"] or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": issue_token(dict(user)), "token_type": "bearer", "role": user["role"], "expires_in": settings.JWT_TTL_MINUTES * 60}


def current_user(request: Request, authorization: str | None = Header(default=None)) -> Dict[str, str]:
    """Dependency to fetch and validate the current authenticated user."""
    if not settings.AUTH_REQUIRED:
        user = {"username": "development-analyst", "role": "analyst"}
        request.state.actor = user["username"]
        request.state.role = user["role"]
        return user
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    try:
        claims = jwt.decode(authorization.removeprefix("Bearer "), settings.jwt_secret, algorithms=["HS256"])
        user = {"username": claims["sub"], "role": claims["role"]}
    except (jwt.PyJWTError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc
    request.state.actor = user["username"]
    request.state.role = user["role"]
    return user


@lru_cache()
def require_roles(*allowed_roles: str):
    """Dependency to check if the user has one of the allowed roles."""
    def dependency(request: Request, authorization: str | None = Header(default=None)) -> Dict[str, str]:
        user = current_user(request, authorization)
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role for this resource")
        return user
    return dependency


def audit_event(*, actor: str, role: str, action: str, resource: str, outcome: str, request_id: str, detail: Dict[str, Any] | None = None) -> None:
    """Write an append-only redacted audit record; never log tokens or private payloads."""
    with connection() as conn:
        conn.execute(
            """INSERT INTO audit_events(occurred_at, actor, role, action, resource, outcome, request_id, detail_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (utc_now(), actor, role, action, resource, outcome, request_id, json.dumps(detail or {}, separators=(",", ":"))),
        )
