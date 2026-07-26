"""Scoring computations for Sentinel's similar case recommendation engine."""

from __future__ import annotations

import math
from datetime import datetime
from typing import List, Set, Any


def jaccard_similarity(set_a: Set[Any], set_b: Set[Any]) -> float:
    """Calculate Jaccard similarity coefficient between two sets."""
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union


def geospatial_similarity(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance-based geospatial similarity score using Haversine formula."""
    if lat1 == 0.0 or lat2 == 0.0:
        return 0.0
        
    # Haversine formula
    R = 6371.0 # Radius of the earth in km
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c # Distance in km
    
    # Map distance to score: 0km -> 1.0, decay exponentially (e.g. 5km decay factor)
    # At 5km distance, score is ~0.37
    return math.exp(-distance / 5.0)


def temporal_similarity(date_str1: str, date_str2: str) -> float:
    """Calculate similarity based on temporal closeness (days difference)."""
    try:
        d1 = datetime.fromisoformat(date_str1.replace("Z", "+00:00"))
        d2 = datetime.fromisoformat(date_str2.replace("Z", "+00:00"))
        delta_days = abs((d1 - d2).days)
        # Decay over time: 30 days difference -> ~0.37
        return math.exp(-delta_days / 30.0)
    except Exception:
        return 0.0


def cosine_similarity_flat(list_a: List[str], list_b: List[str]) -> float:
    """Compute cosine similarity of simple bag-of-words list representations."""
    set_a = set(list_a)
    set_b = set(list_b)
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    
    intersection = len(set_a.intersection(set_b))
    denominator = math.sqrt(len(set_a)) * math.sqrt(len(set_b))
    return intersection / denominator
