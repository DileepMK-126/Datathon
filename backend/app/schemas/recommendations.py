"""Pydantic schemas for Patrol Recommendations validation."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    """Schema representing a single patrol or operational recommendation."""
    id: str = Field(..., description="Unique recommendation ID")
    priority: str = Field(..., description="Severity level: Critical, High, Medium, Low")
    confidence: int = Field(..., description="Confidence score percentage")
    category: str = Field(..., description="Recommendation category")
    summary: str = Field(..., description="Actionable headline summary")
    explanation: str = Field(..., description="Detailed support justification narrative")
    recommended_shift: str = Field(..., description="Recommended patrol shift shift interval")
    duration_hours: int = Field(..., description="Assigned shift hour duration")
    deterrence_level: str = Field(..., description="Estimated visible deterrence value")
    expected_response_reduction: str = Field(..., description="Expected reduction in response times")
    community_trust_index: str = Field(..., description="Estimated community reassurance index")
    supporting_evidence: List[str] = Field(..., description="List of evidence triggers")
    related_cases: List[str] = Field(..., description="Traced historical related cases list")
    related_hotspots: List[str] = Field(..., description="Traced spatial hotspot lists")
    review_required: bool = Field(default=True, description="Human review disclaimer verification flag")


class RecommendationResponse(BaseModel):
    """Schema representing recommendations payload query results."""
    zone_id: str = Field(..., description="Target Zone ID")
    zone_name: str = Field(..., description="Target Zone Name")
    recommendations: List[RecommendationItem] = Field(..., description="List of generated recommendations")
