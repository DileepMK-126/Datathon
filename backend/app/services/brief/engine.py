"""Morning brief orchestrator compiling daily intelligence reports."""

from __future__ import annotations

import time
import logging
from datetime import datetime
from typing import Dict, Any

from .cache import get_cached_brief, set_cached_brief
from .aggregator import aggregate_intelligence_data
from .metrics import calculate_executive_metrics
from .priority import prioritize_active_alerts
from .templates import render_brief_narrative, compile_intelligence_highlights
from .formatter import format_brief_date, format_to_markdown

logger = logging.getLogger("sentinel")


def get_morning_brief(date_str: str | None = None, district: str | None = None) -> Dict[str, Any]:
    """Compile and retrieve the morning command brief, caching outputs."""
    start_time = time.perf_counter()
    
    # 1. Check cache first
    cache_key = f"{date_str or 'today'}:{district or 'all'}"
    cached = get_cached_brief(cache_key)
    if cached is not None:
        logger.info(f"Morning brief cache HIT for key {cache_key}")
        return cached
        
    # 2. Gather intelligence parameters
    aggregated = aggregate_intelligence_data()
    
    # 3. Calculate executive metrics
    metrics = calculate_executive_metrics(aggregated)
    
    # 4. Filter and prioritize alerts
    alerts = prioritize_active_alerts()
    
    # 5. Format natural language brief
    narrative = render_brief_narrative(aggregated, metrics)
    highlights = compile_intelligence_highlights(aggregated, metrics)
    
    dt = datetime.now()
    formatted_date = format_brief_date(dt)
    
    threat_level = "GUARDS"
    score = metrics["overall_threat_score"]
    if score >= 80:
        threat_level = "CRITICAL"
    elif score >= 65:
        threat_level = "HIGH"
    elif score >= 45:
        threat_level = "ELEVATED"
    else:
        threat_level = "GUARDED"
        
    response = {
        "date": formatted_date,
        "threat_level": threat_level,
        "threat_score": score,
        "highest_risk_sector": aggregated["highest_risk_zone_name"],
        "new_hotspots": aggregated["new_hotspots_count"],
        "active_investigations": aggregated["network_connected_cases"] + 4, # baseline offset
        "linked_networks": aggregated["network_connected_cases"],
        "repeat_offenders": aggregated["repeat_offenders_count"],
        "summary": narrative,
        "highlights": highlights,
        "alerts": alerts,
        "metrics": {
            "threat_score": score,
            "risk_trend": metrics["risk_trend"],
            "incident_growth": metrics["incident_growth_percent"],
            "hotspot_growth": metrics["hotspot_growth_count"],
            "network_growth": metrics["network_growth_cases"],
            "recommendation_count": metrics["recommendation_count"]
        },
        "review_required": True,
        "execution_time_seconds": round(time.perf_counter() - start_time, 4)
    }
    
    # Compile markdown representation for easy exporting
    response["markdown"] = format_to_markdown(response)
    
    set_cached_brief(cache_key, response)
    return response
