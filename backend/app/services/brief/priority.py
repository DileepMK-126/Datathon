"""Urgency prioritization and alert sorter for the Morning Brief."""

from __future__ import annotations

from typing import List, Dict, Any
from ..analytics.network import alerts_payload


def prioritize_active_alerts() -> List[Dict[str, Any]]:
    """Prioritize operational alerts sorted by criticality (Critical, High, Medium, Low)."""
    alerts = alerts_payload()
    
    # Map levels to sorting indexes
    level_weights = {
        "critical": 4,
        "high": 3,
        "watch": 2,
        "low": 1
    }
    
    sorted_alerts = sorted(
        alerts,
        key=lambda x: level_weights.get(x.get("level", "low").lower(), 0),
        reverse=True
    )
    
    return sorted_alerts
