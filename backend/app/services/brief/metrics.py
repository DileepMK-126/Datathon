"""Executive metrics calculator for command intelligence reporting."""

from __future__ import annotations

from typing import Dict, Any


def calculate_executive_metrics(aggregated: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate executive indexes: Overall Threat Score, risk trends, and indicators."""
    
    # 1. Overall Threat Score (0 - 100 scale)
    base_threat = aggregated["highest_risk_score"] * 0.6
    hotspot_threat = min(aggregated["new_hotspots_count"] * 10, 20)
    growth_threat = min(max(aggregated["incident_growth_rate"] * 0.5, 0), 20)
    
    threat_score = round(base_threat + hotspot_threat + growth_threat)
    
    # 2. Risk Trend
    if aggregated["incident_growth_rate"] > 10:
        trend = "INCREASING"
    elif aggregated["incident_growth_rate"] < -10:
        trend = "DECREASING"
    else:
        trend = "STABLE"
        
    return {
        "overall_threat_score": min(98, max(5, threat_score)),
        "risk_trend": trend,
        "incident_growth_percent": aggregated["incident_growth_rate"],
        "hotspot_growth_count": aggregated["new_hotspots_count"],
        "network_growth_cases": aggregated["network_connected_cases"],
        "recommendation_count": aggregated["recommendations_count"]
    }
