"""Simple in-memory cache to store computed features and similarity scores."""

from __future__ import annotations

from typing import Any, Dict

# In-memory dictionary caches
_feature_cache: Dict[str, Any] = {}
_similarity_cache: Dict[str, Any] = {}


def get_cached_features(case_id: str) -> Any | None:
    """Retrieve cached feature extraction for a case."""
    return _feature_cache.get(case_id)


def set_cached_features(case_id: str, features: Any) -> None:
    """Cache feature extraction for a case."""
    _feature_cache[case_id] = features


def get_cached_similar_cases(case_id: str, threshold: float, limit: int) -> Any | None:
    """Retrieve cached similarity query result."""
    cache_key = f"{case_id}:{threshold}:{limit}"
    return _similarity_cache.get(cache_key)


def set_cached_similar_cases(case_id: str, threshold: float, limit: int, results: Any) -> None:
    """Cache similarity query result."""
    cache_key = f"{case_id}:{threshold}:{limit}"
    _similarity_cache[cache_key] = results


def clear_similarity_cache() -> None:
    """Clear all cached similarity computations."""
    _feature_cache.clear()
    _similarity_cache.clear()
