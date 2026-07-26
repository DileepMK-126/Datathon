"""Data models representing individual timeline event items and case response collections."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class TimelineEventModel(BaseModel):
    event_id: str
    timestamp: str
    source_system: str
    event_type: str
    title: str
    description: str
    confidence: float
    linked_case: Optional[str] = None
    resolved_entities: List[str] = []
    supporting_evidence: List[str] = []
    severity: str


class TimelineResponseModel(BaseModel):
    case_id: str
    events: List[TimelineEventModel]
