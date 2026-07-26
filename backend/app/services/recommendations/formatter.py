"""Narrative compilers and text formatters for recommendations."""

from __future__ import annotations

from typing import List, Dict, Any


def compile_recommendation_summary(
    category: str, 
    priority: str, 
    zone_name: str
) -> str:
    """Format a clean headline summary statement for the suggestion."""
    return f"Recommended action: {category} in {zone_name} (Priority: {priority})"


def compile_explanation(
    category: str,
    zone_name: str,
    risk_score: float,
    has_hotspot: bool
) -> str:
    """Compile a detailed decision-support reasoning statement for the recommendation."""
    reasons = []
    reasons.append(f"The forecasting model projects an elevated risk level of {risk_score}% in {zone_name}")
    if has_hotspot:
        reasons.append("with active incident clustering detected by spatial DBSCAN operations")
        
    reason_str = " ".join(reasons)
    
    return (
        f"{reason_str}. A targeted operational directive of '{category}' is suggested "
        "to optimize patrol footprints. Human verification is required before dispatching."
    )
