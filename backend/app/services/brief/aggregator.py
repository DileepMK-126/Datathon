"""Intelligence aggregator fetching metrics across Sentinel modules."""

from __future__ import annotations

from typing import Dict, Any, List
from datetime import timedelta
import numpy as np

from ..analytics.risk import risk_payload
from ..analytics.hotspots import hotspot_payload
from ..analytics.anomaly import trend_payload
from ..analytics.network import graph_payload
from ..recommendations.engine import generate_zone_recommendations
from ...db.models import ZONES
from ...db.repositories import CaseRepository, IncidentRepository
from ...utils.helpers import NOW, iso


def aggregate_intelligence_data() -> Dict[str, Any]:
    """Retrieve and aggregate operational statistics from all existing domain services."""
    # 1. Fetch risk and hotspot payloads
    risks = risk_payload()
    hotspots = hotspot_payload()
    
    # 2. Identify top risk zone
    highest_risk_zone = risks[0] if risks else {"zone_id": "sector-7", "zone_name": "Sector 7", "score": 90}
    
    # 3. Sum active recommendations
    recs_count = 0
    for zone in ZONES:
        recs_count += len(generate_zone_recommendations(zone["id"]))
        
    # 4. Analyze timeline incidents growth
    recent_count = len(IncidentRepository.get_incidents_since(iso(NOW - timedelta(days=7))))
    baseline_count = len(IncidentRepository.get_incidents_since(iso(NOW - timedelta(days=14)))) - recent_count
    
    growth_rate = 0.0
    if baseline_count > 0:
        growth_rate = round(((recent_count - baseline_count) / baseline_count) * 100, 1)
        
    # 5. Extract criminal network attributes
    net = graph_payload()
    net_cases = sum(node["kind"] == "case" for node in net["nodes"])
    repeat_offenders = sum(node["kind"] == "person" for node in net["nodes"])
    
    return {
        "highest_risk_zone_id": highest_risk_zone["zone_id"],
        "highest_risk_zone_name": highest_risk_zone["zone_name"],
        "highest_risk_score": highest_risk_zone["score"],
        "new_hotspots_count": len(hotspots),
        "total_hotspots_incidents": sum(h["incident_count"] for h in hotspots),
        "recommendations_count": recs_count,
        "recent_incidents_volume": recent_count,
        "incident_growth_rate": growth_rate,
        "network_connected_cases": net_cases,
        "repeat_offenders_count": repeat_offenders,
        "largest_network_summary": net["summary"]
    }
