"""Sentinel Similar Case Recommendation Engine services."""

from __future__ import annotations

from .engine import get_similar_cases
from .weights import DEFAULT_WEIGHTS
from .cache import clear_similarity_cache

__all__ = ["get_similar_cases", "DEFAULT_WEIGHTS", "clear_similarity_cache"]
