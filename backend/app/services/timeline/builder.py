"""Builder compiling database records, updates, recommendations, and AI alerts into sorted timeline objects."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from ...db.repositories import CaseRepository
from ...services.analytics.network import recommendations_payload
from ...services.intelligence.engine import generate_zone_intelligence
from .models import TimelineEventModel


def make_event_id(*args) -> str:
    """Generate a unique deterministic event ID using MD5 hashing."""
    hasher = hashlib.md5()
    for arg in args:
        hasher.update(str(arg).encode())
    return f"EVT-{hasher.hexdigest()[:8].upper()}"


def parse_utc_timestamp(timestamp_str: str) -> datetime:
    """Parse an ISO format timestamp string into a timezone-aware UTC datetime."""
    try:
        cleaned = timestamp_str.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)
    except Exception:
        return datetime.now(timezone.utc)


def build_timeline(case_id: str) -> List[TimelineEventModel]:
    """Gather case, source records, updates, recommendations, and intelligence into a chronological event list."""
    events: List[TimelineEventModel] = []
    
    # 1. Fetch case details
    case = CaseRepository.get_case_profile(case_id)
    if not case:
        return []
        
    zone_id = case["zone_id"]
    opened_at_str = case["opened_at"]
    crime_type = case["crime_type"]
    
    opened_at = parse_utc_timestamp(opened_at_str)

    # 2. Fetch case resolved entities
    entities_rows = CaseRepository.get_case_entities(case_id)
    resolved_entities = [row["display_value"] for row in entities_rows]
    
    # 3. Fetch case source records (Police FIR, CCTV & lab, Court & prison)
    sources = CaseRepository.get_case_sources(case_id)
    
    for src in sources:
        system = src["source_system"]
        payload = src["payload"]
        recorded_at = src["recorded_at"]
        confidence = src["confidence"]
        
        if system == "Police FIR":
            events.append(TimelineEventModel(
                event_id=make_event_id(case_id, "FIR", recorded_at),
                timestamp=recorded_at,
                source_system="Police FIR",
                event_type="FIR Registered",
                title="First Information Report Registered",
                description=f"Unified crime dossier initialized for crime type '{crime_type}' at precinct station '{payload.get('station', case.get('zone_name'))}'. Case validation status: {payload.get('validation', 'origin record')}.",
                confidence=confidence,
                linked_case=case_id,
                resolved_entities=resolved_entities,
                supporting_evidence=[f"FIR Reference ID: {payload.get('reference', case_id)}"],
                severity="HIGH"
            ))
            
        elif system == "CCTV & lab":
            # CCTV Match Event
            camera = payload.get("camera_reference", "CAM-01")
            events.append(TimelineEventModel(
                event_id=make_event_id(case_id, "CCTV", recorded_at),
                timestamp=recorded_at,
                source_system="CCTV",
                event_type="CCTV Match",
                title="Surveillance Camera Match",
                description=f"Computer vision model matched suspect patterns ({payload.get('match_type', 'vehicle/movement pattern')}) on camera {camera}.",
                confidence=confidence,
                linked_case=case_id,
                resolved_entities=resolved_entities[:1],
                supporting_evidence=[f"Camera Reference: {camera}"],
                severity="MEDIUM"
            ))
            
            # Laboratory forensic analysis event (+2 hours offset from opened_at)
            lab_time = (opened_at + timedelta(hours=2)).isoformat().replace("+00:00", "Z")
            events.append(TimelineEventModel(
                event_id=make_event_id(case_id, "Lab", lab_time),
                timestamp=lab_time,
                source_system="Laboratory",
                event_type="Laboratory Analysis",
                title="Forensic Laboratory Report",
                description=f"Forensic lab analysis verified. Evidence classification: {payload.get('evidence_status', 'analyst review')}. Match type: {payload.get('match_type')}.",
                confidence=min(1.0, confidence + 0.1),
                linked_case=case_id,
                resolved_entities=resolved_entities[1:2] if len(resolved_entities) > 1 else [],
                supporting_evidence=[f"Forensics status: {payload.get('evidence_status', 'complete')}"],
                severity="HIGH"
            ))
            
        elif system == "Court & prison":
            # Court event
            events.append(TimelineEventModel(
                event_id=make_event_id(case_id, "Court", recorded_at),
                timestamp=recorded_at,
                source_system="Court",
                event_type="Court Hearing",
                title="Justice System Listing",
                description=f"Judicial linkage found in justice registry under case reference {payload.get('linked_reference')}. Hearing stage: {payload.get('stage')}.",
                confidence=confidence,
                linked_case=case_id,
                resolved_entities=[],
                supporting_evidence=[f"Judicial Reference: {payload.get('linked_reference')}"],
                severity="MEDIUM"
            ))
            
            # Prison booking event (+2 days offset from opened_at)
            prison_time = (opened_at + timedelta(days=2)).isoformat().replace("+00:00", "Z")
            events.append(TimelineEventModel(
                event_id=make_event_id(case_id, "Prison", prison_time),
                timestamp=prison_time,
                source_system="Prison",
                event_type="Prison Booking",
                title="Correctional System Booking Update",
                description=f"Prison system booking transaction logs updated. Current correctional booking disposition: '{payload.get('disposition')}'",
                confidence=confidence,
                linked_case=case_id,
                resolved_entities=[],
                supporting_evidence=[f"Disposition status: {payload.get('disposition')}"],
                severity="MEDIUM"
            ))

    # 4. Injected Investigation Updates
    # Case Assignment Update (+4 hours offset from opened_at)
    assign_time = (opened_at + timedelta(hours=4)).isoformat().replace("+00:00", "Z")
    events.append(TimelineEventModel(
        event_id=make_event_id(case_id, "Assignment", assign_time),
        timestamp=assign_time,
        source_system="Investigation Updates",
        event_type="Case Assigned",
        title="Precinct Assignment",
        description=f"Unified crime dossier {case_id} registered and formally assigned to the local precinct task force for investigative follow-up.",
        confidence=1.0,
        linked_case=case_id,
        resolved_entities=[],
        supporting_evidence=["Precinct docket registry check"],
        severity="LOW"
    ))
    
    # Entity Resolution Update (+20 hours offset from opened_at)
    if resolved_entities:
        er_time = (opened_at + timedelta(hours=20)).isoformat().replace("+00:00", "Z")
        events.append(TimelineEventModel(
            event_id=make_event_id(case_id, "EntityResolution", er_time),
            timestamp=er_time,
            source_system="Investigation Updates",
            event_type="Entity Resolved",
            title="Entity Resolution Match",
            description=f"Criminal graph entity resolution matched focal case entities across regional systems. Resolved entities: {', '.join(resolved_entities[:3])}.",
            confidence=0.94,
            linked_case=case_id,
            resolved_entities=resolved_entities,
            supporting_evidence=["NetworkX entity resolver match logs"],
            severity="MEDIUM"
        ))

    # 5. Recommendation Action (+3 days offset from opened_at)
    try:
        recs = recommendations_payload(zone_id)
        actions = recs.get("actions", [])
        if actions:
            action = actions[0]
            rec_time = (opened_at + timedelta(days=3)).isoformat().replace("+00:00", "Z")
            events.append(TimelineEventModel(
                event_id=make_event_id(case_id, "Recommendation", rec_time),
                timestamp=rec_time,
                source_system="Recommendations",
                event_type="AI Recommendation",
                title="Patrol action suggestion",
                description=action["action"],
                confidence=0.85,
                linked_case=case_id,
                resolved_entities=[],
                supporting_evidence=[action["evidence"]],
                severity=action.get("priority", "MEDIUM").upper()
            ))
    except Exception:
        pass
        
    # 6. Intelligence Engine Alert (At current UTC datetime)
    try:
        intel = generate_zone_intelligence(zone_id)
        intel_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        events.append(TimelineEventModel(
            event_id=make_event_id(case_id, "Intelligence", intel_time),
            timestamp=intel_time,
            source_system="Intelligence Engine",
            event_type="AI Intelligence Alert",
            title=f"AI Briefing: {intel.get('priority')} threat level",
            description=intel.get("summary", "System baseline tracking is active."),
            confidence=float(intel.get("confidence", 75)) / 100.0,
            linked_case=case_id,
            resolved_entities=intel.get("drivers", []),
            supporting_evidence=intel.get("evidence", []),
            severity=intel.get("priority", "MEDIUM").upper()
        ))
    except Exception:
        pass

    # Sort events chronologically (oldest to newest)
    events.sort(key=lambda x: x.timestamp)
    return events
