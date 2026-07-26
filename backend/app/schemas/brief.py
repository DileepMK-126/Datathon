"""Pydantic schemas for Morning Intelligence Brief responses."""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class BriefMetrics(BaseModel):
    """Schema representing executive metrics indicators."""
    threat_score: int = Field(..., description="Overall computed threat score index")
    risk_trend: str = Field(..., description="Trend direction: INCREASING, DECREASING, STABLE")
    incident_growth: float = Field(..., description="Incident growth rate vs. baseline")
    hotspot_growth: int = Field(..., description="Active hotspot clusters count")
    network_growth: int = Field(..., description="Active networks size count")
    recommendation_count: int = Field(..., description="Active patrol recommendations count")


class AlertDetail(BaseModel):
    """Schema representing prioritized active alert indicators."""
    id: str
    type: str
    level: str
    zone_id: str
    title: str
    text: str
    confidence: int
    linked_records: int
    detected: str


class MorningBriefResponse(BaseModel):
    """Schema representing the completed Morning Command Brief."""
    date: str = Field(..., description="Formatted calendar date")
    threat_level: str = Field(..., description="Threat rating description: CRITICAL, HIGH, ELEVATED, GUARDED")
    threat_score: int = Field(..., description="Threat index score out of 100")
    highest_risk_sector: str = Field(..., description="Top risk sector zone name")
    new_hotspots: int = Field(..., description="Active hotspots count")
    active_investigations: int = Field(..., description="Active cases volume")
    linked_networks: int = Field(..., description="Active networks count")
    repeat_offenders: int = Field(..., description="Active resolved repeat offenders count")
    summary: str = Field(..., description="Natural language intelligence summary paragraph")
    highlights: List[str] = Field(..., description="Bullet points highlights")
    alerts: List[AlertDetail] = Field(..., description="Prioritized operational alerts list")
    metrics: BriefMetrics = Field(..., description="Key numerical indexes")
    markdown: str = Field(..., description="Report layout in Markdown layout format")
    review_required: bool = Field(default=True, description="Human review advisory verification flag")
    execution_time_seconds: float = Field(..., description="Calculated elapsed duration")
