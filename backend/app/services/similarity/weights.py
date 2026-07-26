"""Configurable weights for the Similar Case Recommendation Engine."""

from __future__ import annotations

from typing import Dict

# Weights must sum to 1.0 (100%)
DEFAULT_WEIGHTS: Dict[str, float] = {
    "crime_type": 0.25,
    "location": 0.20,
    "entity_match": 0.20,
    "timeline": 0.10,
    "network": 0.10,
    "vehicle": 0.05,
    "phone": 0.05,
    "risk_zone": 0.05,
}
