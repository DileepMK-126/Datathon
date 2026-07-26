"""In-memory cache for computed patrol recommendations."""

from __future__ import annotations

from typing import Any, Dict

# Cache mapping zone_ids and case_ids to recommendation lists
_zone_recommendations_cache: Dict[str, Any] = {}
_case_recommendations_cache: Dict[str, Any] = {}


def get_cached_zone_recommendations(zone_id: str) -> Any | None:
    """Retrieve cached recommendations for a zone."""
    return _zone_recommendations_cache.get(zone_id)


def set_cached_zone_recommendations(zone_id: str, data: Any) -> None:
    """Cache recommendations for a zone."""
    _zone_recommendations_cache[zone_id] = data


def get_cached_case_recommendations(case_id: str) -> Any | None:
    """Retrieve cached recommendations for a case."""
    return _case_recommendations_cache.get(case_id)


def set_cached_case_recommendations(case_id: str, data: Any) -> None:
    """Cache recommendations for a case."""
    _case_recommendations_cache[case_id] = data


def clear_recommendations_cache() -> None:
    """Clear cached recommendations."""
    _zone_recommendations_cache.clear()
    _case_recommendations_cache.clear()
