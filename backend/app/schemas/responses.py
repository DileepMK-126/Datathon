"""Pydantic response models for standard API JSON outputs."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    data_mode: str
    auth_required: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    expires_in: int


class IntelligenceResponse(BaseModel):
    zone_id: str
    zone_name: str
    priority: str
    confidence: int
    summary: str
    drivers: List[str]
    evidence: List[str]
    recommendations: List[str]
    review_required: bool


class TimelineEvent(BaseModel):
    event_id: str
    timestamp: str
    source_system: str
    event_type: str
    title: str
    description: str
    confidence: float
    linked_case: str | None = None
    resolved_entities: List[str] = []
    supporting_evidence: List[str] = []
    severity: str


class TimelineResponse(BaseModel):
    case_id: str
    events: List[TimelineEvent]

