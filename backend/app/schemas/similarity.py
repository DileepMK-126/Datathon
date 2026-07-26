"""Pydantic schemas for the Similar Case Recommendation Engine."""

from __future__ import annotations

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class SimilarityRequest(BaseModel):
    """Schema for custom similarity matching parameters."""
    threshold: float = Field(default=75.0, ge=0.0, le=100.0, description="Similarity threshold percentage")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum number of matches to return")
    weights: Dict[str, float] = Field(default=None, description="Custom weights configuration mapping category to decimal weight")


class SimilarityMatch(BaseModel):
    """Schema representing a single similar case match record."""
    case_id: str = Field(..., description="Target similar Case ID")
    crime_type: str = Field(..., description="Crime classification")
    similarity_score: float = Field(..., description="Weighted composite score out of 100")
    confidence: str = Field(..., description="Similarity confidence category description")
    reasoning: str = Field(..., description="Explainable AI reasoning string")
    shared_entities: Dict[str, List[str]] = Field(..., description="Matched shared entities grouped by type")
    subscores: Dict[str, float] = Field(..., description="Detailed individual component similarity scores")
    details: Dict[str, Any] = Field(..., description="Expanded historical case attributes detail map")


class SimilarityResponse(BaseModel):
    """API response schema for case similarities queries."""
    case_id: str = Field(..., description="Focal Case ID")
    total_matches: int = Field(..., description="Total matches returning above threshold")
    matches: List[SimilarityMatch] = Field(..., description="Array of similar cases matches ordered by score")
    execution_time_seconds: float = Field(..., description="Similarity evaluation duration in seconds")
