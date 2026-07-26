"""In-memory cache for daily morning intelligence briefs."""

from __future__ import annotations

from typing import Any, Dict

# Cache mapping queries to compiled brief dicts
_brief_cache: Dict[str, Any] = {}


def get_cached_brief(key: str) -> Any | None:
    """Retrieve a cached morning brief payload."""
    return _brief_cache.get(key)


def set_cached_brief(key: str, data: Any) -> None:
    """Cache morning brief payload."""
    _brief_cache[key] = data


def clear_brief_cache() -> None:
    """Clear cached briefs."""
    _brief_cache.clear()
