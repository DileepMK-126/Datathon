"""In-memory cache for computed SHAP attributions and explanations."""

from __future__ import annotations

from typing import Any, Dict

# In-memory dictionary caches
_shap_cache: Dict[str, Any] = {}
_explanation_cache: Dict[str, Any] = {}


def get_cached_shap(zone_id: str) -> Any | None:
    """Retrieve cached SHAP values for a zone."""
    return _shap_cache.get(zone_id)


def set_cached_shap(zone_id: str, shap_values: Any) -> None:
    """Cache SHAP values for a zone."""
    _shap_cache[zone_id] = shap_values


def get_cached_explanation(zone_id: str, days: int) -> Any | None:
    """Retrieve cached formatted explanation payload."""
    key = f"{zone_id}:{days}"
    return _explanation_cache.get(key)


def set_cached_explanation(zone_id: str, days: int, explanation: Any) -> None:
    """Cache formatted explanation payload."""
    key = f"{zone_id}:{days}"
    _explanation_cache[key] = explanation


def clear_explainability_cache() -> None:
    """Clear all cached explainability data."""
    _shap_cache.clear()
    _explanation_cache.clear()
