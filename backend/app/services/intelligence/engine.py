"""Orchestrator for the Intelligence Engine linking multiple analytics engines."""

from __future__ import annotations

import time
from typing import Any, Dict

from ...core.logging import logger
from ...db.models import ZONE_INDEX, ZONES
from ..analytics.hotspots import hotspot_payload
from ..analytics.risk import risk_payload
from ..analytics.anomaly import trend_payload
from ..analytics.network import graph_payload, recommendations_payload
from .summary import format_intelligence_payload


def generate_zone_intelligence(zone_id: str) -> Dict[str, Any]:
    """Gather metrics from all analytical subsystems and construct a unified intelligence report."""
    start_time = time.perf_counter()
    logger.info("Triggered intelligence brief generation for zone: %s", zone_id)
    
    # Verify zone validity
    zone = ZONE_INDEX.get(zone_id)
    if not zone:
        logger.error("Failed to generate intelligence: unknown zone: %s", zone_id)
        # Return fallback default response
        return get_fallback_payload(zone_id, f"Unknown Zone ({zone_id})")
        
    zone_name = zone["name"]
    
    # 1. Hotspots
    try:
        hotspots = hotspot_payload()
        hotspot = next((item for item in hotspots if item["zone_id"] == zone_id), {})
        logger.info("Hotspot Service queried successfully.")
    except Exception as exc:
        logger.error("Hotspot Service failed: %s", exc)
        hotspot = {}
        
    # 2. Risk
    try:
        risks = risk_payload()
        risk = next((item for item in risks if item["zone_id"] == zone_id), {})
        logger.info("Risk Service queried successfully.")
    except Exception as exc:
        logger.error("Risk Service failed: %s", exc)
        risk = {}
        
    # 3. Anomaly Trend
    try:
        trend = trend_payload(zone_id)
        logger.info("Trend Service queried successfully.")
    except Exception as exc:
        logger.error("Trend Service failed: %s", exc)
        trend = {}
        
    # 4. Network Linkage Graph
    try:
        network = graph_payload()
        logger.info("Network Service queried successfully.")
    except Exception as exc:
        logger.error("Network Service failed: %s", exc)
        network = {}
        
    # 5. Patrol Recommendations
    try:
        recommendations = recommendations_payload(zone_id)
        logger.info("Recommendations Service queried successfully.")
    except Exception as exc:
        logger.error("Recommendations Service failed: %s", exc)
        recommendations = {}
        
    # Build payload using formatted templates
    try:
        payload = format_intelligence_payload(
            zone_id=zone_id,
            zone_name=zone_name,
            hotspot=hotspot,
            risk=risk,
            trend=trend,
            network=network,
            recommendations=recommendations,
        )
        duration = time.perf_counter() - start_time
        logger.info(
            "Intelligence engine execution completed in %.4f seconds. Matched Priority: %s, Confidence: %d%%",
            duration,
            payload["priority"],
            payload["confidence"],
        )
        return payload
    except Exception as exc:
        logger.error("Failed to format intelligence summary: %s", exc)
        return get_fallback_payload(zone_id, zone_name)


def get_fallback_payload(zone_id: str, zone_name: str) -> Dict[str, Any]:
    """Construct an empty fallback structure in case of total execution errors."""
    return {
        "zone_id": zone_id,
        "zone_name": zone_name,
        "priority": "LOW",
        "confidence": 50,
        "summary": f"System monitoring report for {zone_name}. Baseline tracking is currently active.",
        "drivers": [],
        "evidence": ["Baseline automated checks active"],
        "recommendations": ["Validate status with the operations center"],
        "review_required": True,
    }
