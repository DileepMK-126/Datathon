"""Natural language deterministic templates for daily briefings."""

from __future__ import annotations

from typing import Dict, Any, List


def render_brief_narrative(aggregated: Dict[str, Any], metrics: Dict[str, Any]) -> str:
    """Generate a clean, deterministic natural language summary of the morning intelligence picture."""
    zone_name = aggregated["highest_risk_zone_name"]
    score = aggregated["highest_risk_score"]
    growth = aggregated["incident_growth_rate"]
    hotspots = aggregated["new_hotspots_count"]
    network_summary = aggregated["largest_network_summary"]
    
    direction = "increased" if growth >= 0 else "decreased"
    abs_growth = abs(growth)
    
    narrative = (
        f"Operational intelligence indicates that overall crime activity has {direction} "
        f"by {abs_growth}% compared to the baseline period. The highest risk is centered in "
        f"{zone_name} (risk score: {score}%) with {hotspots} active hotspot clusters detected by spatial DBSCAN. "
        f"{network_summary} Risk remains elevated because patrol coverage in this sector is below the target average."
    )
    
    return narrative


def compile_intelligence_highlights(aggregated: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
    """Compile key bullet points highlighting intelligence events."""
    highlights = []
    
    growth = aggregated["incident_growth_rate"]
    direction = "increase" if growth >= 0 else "decrease"
    highlights.append(f"Incident volume changes represent a {abs(growth)}% {direction} vs. baseline.")
    
    highlights.append(f"Detected {aggregated['new_hotspots_count']} spatial crime hotspots requiring immediate patrol review.")
    
    highlights.append(f"Linked network analysis identified {aggregated['repeat_offenders_count']} active repeat offender profiles.")
    
    highlights.append("Recommended action priority: Increase night patrols to mitigate cover gaps.")
    
    return highlights
