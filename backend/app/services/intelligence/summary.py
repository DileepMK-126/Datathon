"""Formatter compiling rule matches and templates into unified summary payloads."""

from __future__ import annotations

from typing import Any, Dict, List

from .rules import evaluate_priority, calculate_confidence
from .templates import (
    get_hotspot_text,
    get_network_text,
    get_risk_text,
    get_trend_text,
    assemble_investigation_summary,
)


def format_intelligence_payload(
    zone_id: str,
    zone_name: str,
    hotspot: Dict[str, Any],
    risk: Dict[str, Any],
    trend: Dict[str, Any],
    network: Dict[str, Any],
    recommendations: Dict[str, Any],
) -> Dict[str, Any]:
    """Assemble individual analytics data payloads into a cohesive priority-ranked report."""
    risk_score = risk.get("score", 0)
    risk_label = risk.get("label", "Guarded")
    risk_horizon = risk.get("horizon_hours", 6)
    risk_confidence = risk.get("confidence", 60)
    risk_drivers = risk.get("drivers", [])
    
    top_driver_name = risk_drivers[0]["name"] if risk_drivers else "Recent incident frequency"
    
    anomaly_detected = trend.get("anomaly", {}).get("detected", False)
    trend_baseline = trend.get("baseline", 0.0)
    period_days = trend.get("period_days", 28)
    
    incident_count = hotspot.get("incident_count", 0)
    hotspot_change = hotspot.get("change_percent", 0)
    hotspot_tone = hotspot.get("tone", "watch")
    
    # Calculate nodes/cases count in NetworkX component
    nodes = network.get("nodes", [])
    case_count = sum(node.get("kind") == "case" for node in nodes)
    entities_count = len(nodes) - case_count
    
    # Evaluate priority & confidence
    priority = evaluate_priority(risk_score, anomaly_detected, incident_count)
    confidence = calculate_confidence(risk_confidence, anomaly_detected, case_count, hotspot_change)
    
    # Generate templates texts
    hotspot_txt = get_hotspot_text(zone_name, "burglary", incident_count, hotspot_change)
    network_txt = get_network_text(case_count, entities_count)
    trend_txt = get_trend_text(anomaly_detected, trend_baseline, period_days)
    risk_txt = get_risk_text(risk_score, risk_label, risk_horizon, top_driver_name)
    
    summary = assemble_investigation_summary(hotspot_txt, network_txt, trend_txt, risk_txt)
    
    # Compile evidence list
    evidence = []
    if incident_count > 0:
        evidence.append(f"DBSCAN hotspot cluster containing {incident_count} records in {zone_name}")
    if anomaly_detected:
        evidence.append(f"Isolation Forest volume anomaly flagged in history trends")
    if risk_score > 0:
        evidence.append(f"Random Forest classification risk score {risk_score}/100")
    if case_count >= 2:
        evidence.append(f"NetworkX shared-entity criminal graph links {case_count} cases")
        
    return {
        "zone_id": zone_id,
        "zone_name": zone_name,
        "priority": priority,
        "confidence": confidence,
        "summary": summary,
        "drivers": [driver["name"] for driver in risk_drivers],
        "evidence": evidence,
        "recommendations": [action["action"] for action in recommendations.get("actions", [])],
        "review_required": True,
    }
