"""Geospatial calculations and constant definitions."""

from __future__ import annotations

# Bounding box coordinates verification helper if needed in future expansions
def is_valid_bbox(min_lng: float, min_lat: float, max_lng: float, max_lat: float) -> bool:
    """Validate bounding box coordinates boundary conditions."""
    return -180.0 <= min_lng <= 180.0 and -180.0 <= max_lng <= 180.0 and -90.0 <= min_lat <= 90.0 and -90.0 <= max_lat <= 90.0
