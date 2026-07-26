"""Priority evaluator for operational patrol recommendations."""

from __future__ import annotations

from typing import Dict, Any


def determine_recommendation_priority(
    risk_score: float,
    has_hotspot: bool = False,
    crime_volume_above_baseline: bool = False
) -> Dict[str, Any]:
    """Calculate the priority label (Critical, High, Medium, Low) and confidence metrics."""
    
    # Priority determination logic
    if risk_score >= 80 and has_hotspot:
        priority = "Critical"
        confidence = 95
    elif risk_score >= 65 or (has_hotspot and crime_volume_above_baseline):
        priority = "High"
        confidence = 88
    elif risk_score >= 45 or has_hotspot:
        priority = "Medium"
        confidence = 78
    else:
        priority = "Low"
        confidence = 65
        
    return {
        "priority": priority,
        "confidence": confidence
    }
