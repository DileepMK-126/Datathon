"""Router for dashboard analytics and metrics summary."""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends

from ..core.security import require_roles
from ..db.models import ZONES
from ..db.repositories import IncidentRepository
from ..services.analytics.hotspots import hotspot_payload
from ..services.analytics.network import graph_payload
from ..services.analytics.risk import risk_payload
from ..utils.helpers import NOW, iso

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard(user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))) -> Dict[str, Any]:
    """Retrieve summarized analytical dashboard metrics for duty officers."""
    risks = risk_payload()
    hotspots = hotspot_payload()
    
    current = IncidentRepository.get_zone_counts(iso(NOW - timedelta(days=7)), iso(NOW), ZONES)
    previous = IncidentRepository.get_zone_counts(iso(NOW - timedelta(days=14)), iso(NOW - timedelta(days=7)), ZONES)
    
    active = sum(current.values())
    prior = sum(previous.values())
    graph = graph_payload()
    
    return {
        "generated_at": iso(NOW), "data_mode": "Synthetic, privacy-safe demo data",
        "metrics": {
            "active_incidents": active, "incident_change_percent": round((active - prior) / max(prior, 1) * 100, 1),
            "emerging_hotspots": len([item for item in hotspots if item["risk_score"] >= 45]),
            "linked_case_clusters": len([node for node in graph["nodes"] if node["kind"] == "case"]),
            "high_risk_zones": len([item for item in risks if item["score"] >= 65]),
        },
        "risks": risks, "human_review_required": True,
    }
