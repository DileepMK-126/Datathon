"""Rule engine compiling matching logic for patrol recommendations."""

from __future__ import annotations

from typing import List, Dict, Any


def evaluate_patrol_rules(
    risk_score: float,
    has_hotspot: bool,
    night_share: float,
    patrol_gap: float,
    network_size: int = 0
) -> List[Dict[str, Any]]:
    """Evaluate and match rules to return suggested recommendation actions."""
    matches = []
    
    # Rule 1: Night patrols
    if risk_score >= 70 or (has_hotspot and night_share >= 0.55):
        matches.append({
            "category": "Increase night patrol",
            "rule_id": "rule-night-patrol",
            "trigger_reason": "High forecasted night-time activity and risk levels."
        })
        
    # Rule 2: Mobile patrols
    if risk_score >= 60 and has_hotspot:
        matches.append({
            "category": "Deploy mobile patrol",
            "rule_id": "rule-mobile-patrol",
            "trigger_reason": "DBSCAN hotspot overlap and elevated local risk forecasting."
        })
        
    # Rule 3: Regular frequency increase
    if patrol_gap >= 0.40:
        matches.append({
            "category": "Increase patrol frequency",
            "rule_id": "rule-frequency-increase",
            "trigger_reason": "High patrol coverage gap in the zone."
        })
        
    # Rule 4: Case investigation reviews
    if network_size >= 4:
        matches.append({
            "category": "Review linked investigations",
            "rule_id": "rule-linked-cases-review",
            "trigger_reason": "Active entity resolve overlap linking multiple recent case files."
        })
        
    # Fallback default if no other matches
    if not matches:
        matches.append({
            "category": "Schedule follow-up review",
            "rule_id": "rule-followup-schedule",
            "trigger_reason": "Standard periodic review of active zone statistics."
        })
        
    return matches
