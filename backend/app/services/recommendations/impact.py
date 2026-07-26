"""Operational impact estimators for patrol recommendation deployments."""

from __future__ import annotations

from typing import Dict, Any


def estimate_recommendation_impact(
    category: str, 
    priority: str
) -> Dict[str, Any]:
    """Estimate operational deterrence, response time reduction, and community impact indicators."""
    
    # Defaults
    deterrence = "Moderate"
    response_reduction = "10% - 15%"
    community_impact = "Neutral"
    
    cat = category.lower()
    
    if "night patrol" in cat or "frequency" in cat:
        deterrence = "High" if priority in ["Critical", "High"] else "Moderate"
        response_reduction = "20% - 25%"
        community_impact = "Highly Reassuring"
    elif "cctv" in cat or "surveillance" in cat:
        deterrence = "High (Indirect)"
        response_reduction = "N/A"
        community_impact = "Supportive"
    elif "investigation" in cat or "linked" in cat:
        deterrence = "N/A"
        response_reduction = "N/A"
        community_impact = "Procedural"
        
    return {
        "deterrence_level": deterrence,
        "expected_response_reduction": response_reduction,
        "community_trust_index": community_impact
    }
