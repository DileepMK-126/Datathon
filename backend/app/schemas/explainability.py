"""Pydantic schemas for the Explainable AI (XAI) Risk module."""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvidenceLink(BaseModel):
    """Schema representing traceable raw evidence supporting a feature."""
    type: str = Field(..., description="Type of evidence: incident, context")
    id: str = Field(..., description="Unique identifier of the record")
    description: str = Field(..., description="Human-readable description of the evidence")
    link: str = Field(..., description="API endpoint to fetch complete record detail")


class DriverExplanation(BaseModel):
    """Schema representing attribution score details for a single feature."""
    feature: str = Field(..., description="Attributed feature name")
    impact: float = Field(..., description="Attribution impact magnitude in percentage")
    direction: str = Field(..., description="Attribution direction: positive, negative")
    value: float = Field(..., description="Observed feature value scale")
    evidence: List[EvidenceLink] = Field(default=[], description="List of evidence items contributing to the feature state")


class ConfidenceDetail(BaseModel):
    """Certainty evaluation parameters metrics."""
    model_certainty: float = Field(..., description="Certainty score out of 100")
    feature_completeness: float = Field(..., description="Completeness of input features")
    historical_consistency: float = Field(..., description="Historical predictability index")
    stability_score: float = Field(..., description="Stability metric out of 100")


class ExplainabilityResponse(BaseModel):
    """API response schema for model explanation queries."""
    zone_id: str = Field(..., description="Target Zone ID")
    zone_name: str = Field(..., description="Target Zone Name")
    risk: int = Field(..., description="Overall calculated risk score")
    confidence: int = Field(..., description="Confidence score out of 100")
    confidence_level: str = Field(..., description="Certainty level description: Very High, High, Medium, Low")
    confidence_metrics: ConfidenceDetail = Field(..., description="Underlying confidence evaluation components")
    drivers: List[DriverExplanation] = Field(..., description="Sorted features by absolute impact")
    positive_contributors: List[DriverExplanation] = Field(..., description="Features with positive risk impact")
    negative_contributors: List[DriverExplanation] = Field(..., description="Features with negative risk impact")
    summary: str = Field(..., description="Dynamic human-readable narrative explanation")
    execution_time_seconds: float = Field(..., description="Execution calculation elapsed duration")
