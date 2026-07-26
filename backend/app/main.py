"""Sentinel: FastAPI web application main entry point."""

from __future__ import annotations

import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    auth,
    dashboard,
    health,
    hotspots,
    risks,
    trends,
    alerts,
    cases,
    networks,
    recommendations,
    audit,
    integrations,
    geospatial,
    intelligence,
    timeline,
    similarity,
    explainability,
    network,
    brief,
    demo,
)
from .core.config import settings
from .core.security import audit_event
from .db.seeder import initialize_database

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    """Run initial database setups and seeder triggers on server startup."""
    initialize_database()


@app.middleware("http")
async def audited_request(request: Request, call_next):
    """Audit logging HTTP middleware tracking resource requests and actor roles."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    try:
        response = await call_next(request)
        outcome = str(response.status_code)
    except Exception:
        try:
            audit_event(
                actor=getattr(request.state, "actor", "anonymous"),
                role=getattr(request.state, "role", "unauthenticated"),
                action=request.method,
                resource=request.url.path,
                outcome="500",
                request_id=request_id
            )
        finally:
            raise
            
    if request.url.path.startswith("/api/") and request.url.path != "/api/health":
        try:
            audit_event(
                actor=getattr(request.state, "actor", "anonymous"),
                role=getattr(request.state, "role", "unauthenticated"),
                action=request.method,
                resource=request.url.path,
                outcome=outcome,
                request_id=request_id
            )
        except Exception:
            pass
            
    response.headers["X-Request-ID"] = request_id
    return response


# Register Domain Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(hotspots.router)
app.include_router(risks.router)
app.include_router(trends.router)
app.include_router(alerts.router)
app.include_router(cases.router)
app.include_router(networks.router)
app.include_router(recommendations.router)
app.include_router(audit.router)
app.include_router(integrations.router)
app.include_router(geospatial.router)
app.include_router(intelligence.router)
app.include_router(timeline.router)
app.include_router(similarity.router)
app.include_router(explainability.router)
app.include_router(network.router)
app.include_router(brief.router)
app.include_router(demo.router)
