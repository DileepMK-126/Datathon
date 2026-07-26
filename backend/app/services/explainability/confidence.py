"""Confidence evaluation engine for risk predictions."""

from __future__ import annotations

from typing import List, Any


def evaluate_confidence(
    probability: float,
    feature_completeness: float = 1.0,
    historical_consistency: float = 0.9,
    stability_score: float = 0.95
) -> dict[str, Any]:
    """Calculate confidence score and category description."""
    
    # Model certainty: max certainty at 0.0 and 1.0, lowest at 0.5
    certainty = 1.0 - (2.0 * abs(probability - 0.5))
    certainty_score = 1.0 - certainty # Transform to 1.0 being high certainty
    
    # Combined score
    composite = (certainty_score * 0.4) + (feature_completeness * 0.2) + (historical_consistency * 0.2) + (stability_score * 0.2)
    composite_percent = round(composite * 100)
    
    if composite_percent >= 85:
        level = "Very High"
    elif composite_percent >= 70:
        level = "High"
    elif composite_percent >= 50:
        level = "Medium"
    else:
        level = "Low"
        
    return {
        "score": composite_percent,
        "level": level,
        "metrics": {
            "model_certainty": round(certainty_score * 100),
            "feature_completeness": round(feature_completeness * 100),
            "historical_consistency": round(historical_consistency * 100),
            "stability_score": round(stability_score * 100)
        }
    }
