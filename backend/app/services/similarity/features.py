"""Feature extraction service for Sentinel cases similarity model."""

from __future__ import annotations

import re
import json
from typing import Any, Dict, List, Set
from ...db.connection import connection
from ...db.repositories import CaseRepository
from ...services.analytics.risk import risk_payload
from ...services.analytics.hotspots import hotspot_payload

WEAPONS_KEYWORDS = ["gun", "pistol", "revolver", "firearm", "knife", "dagger", "blade", "rod", "stick", "weapon"]
EVIDENCE_KEYWORDS = ["cctv", "fingerprint", "dna", "phone", "sim", "license", "vehicle", "footage", "witness"]


def extract_features(case_id: str) -> Dict[str, Any] | None:
    """Extract full feature set for a single case ID."""
    with connection() as conn:
        # 1. Fetch case profile
        case = conn.execute(
            "SELECT id, zone_id, opened_at, status, summary, crime_type FROM cases WHERE id = ?",
            (case_id,)
        ).fetchone()
        
        if not case:
            return None
            
        case_dict = dict(case)
        
        # 2. Fetch incident details
        incident = conn.execute(
            "SELECT latitude, longitude, occurred_at, narrative FROM incidents WHERE case_id = ?",
            (case_id,)
        ).fetchone()
        
        incident_dict = dict(incident) if incident else {}
        
        # 3. Fetch case entities
        entities = conn.execute(
            "SELECT entity_type, normalized_value, display_value FROM case_entities WHERE case_id = ?",
            (case_id,)
        ).fetchall()
        
        # Group entities
        persons: Set[str] = set()
        phones: Set[str] = set()
        vehicles: Set[str] = set()
        addresses: Set[str] = set()
        
        for ent in entities:
            etype = ent["entity_type"]
            val = ent["normalized_value"]
            if etype == "person":
                persons.add(val)
            elif etype == "phone":
                phones.add(val)
            elif etype == "vehicle":
                vehicles.add(val)
            elif etype == "address":
                addresses.add(val)
                
        # 4. Repeat Offender Flag: Check if any person in this case has other cases
        repeat_offender = False
        if persons:
            placeholders = ",".join("?" for _ in persons)
            query = f"""
                SELECT COUNT(DISTINCT case_id) AS cnt 
                FROM case_entities 
                WHERE entity_type = 'person' AND normalized_value IN ({placeholders}) AND case_id != ?
            """
            params = list(persons) + [case_id]
            res = conn.execute(query, params).fetchone()
            if res and res["cnt"] > 0:
                repeat_offender = True
                
        # 5. Extract Weapons & Evidence Tags from narrative and summary
        combined_text = (case_dict.get("summary") or "") + " " + (incident_dict.get("narrative") or "")
        combined_text_lower = combined_text.lower()
        
        weapons = [w for w in WEAPONS_KEYWORDS if w in combined_text_lower]
        evidence_tags = [e for e in EVIDENCE_KEYWORDS if e in combined_text_lower]
        
        # 6. Fetch Court Outcomes & Prison records
        sources = conn.execute(
            "SELECT source_system, record_type, payload_json FROM source_records WHERE case_id = ?",
            (case_id,)
        ).fetchall()
        
        court_outcome = "Pending"
        prison_history = False
        
        for src in sources:
            source_system = src["source_system"].lower()
            record_type = src["record_type"].lower()
            try:
                payload = json.loads(src["payload_json"]) if isinstance(src["payload_json"], str) else src["payload_json"]
            except Exception:
                payload = {}
                
            if "court" in source_system or "court" in record_type:
                court_outcome = payload.get("outcome") or payload.get("disposition") or "Pending"
            if "prison" in source_system or "prison" in record_type:
                prison_history = True

    # 7. Timeline events count
    timeline_pattern = len(sources) + (1 if incident_dict else 0)
    
    # 8. Linked network size from DB connections
    linked_cases = len(CaseRepository.get_linked_cases(case_id, limit=50))
    
    # 9. Get Risk Zone details
    zone_id = case_dict["zone_id"]
    risk_score = 50.0
    try:
        risks = risk_payload()
        for r in risks:
            if r["zone_id"] == zone_id:
                risk_score = r["score"]
                break
    except Exception:
        pass
        
    # 10. Hotspot cluster label
    hotspot_id = "none"
    try:
        hotspots = hotspot_payload()
        for h in hotspots:
            if h["zone_id"] == zone_id:
                hotspot_id = h["id"]
                break
    except Exception:
        pass

    # Extract occurred datetime details
    occurred_at_str = incident_dict.get("occurred_at") or case_dict.get("opened_at")
    from datetime import datetime
    try:
        # Strip trailing Z/offset
        clean_date = occurred_at_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_date)
        day_of_week = dt.strftime("%A")
        incident_time = dt.strftime("%H:%M")
        incident_date = dt.strftime("%Y-%m-%d")
    except Exception:
        day_of_week = "Unknown"
        incident_time = "00:00"
        incident_date = occurred_at_str[:10] if occurred_at_str else "Unknown"

    # Category matching
    crime_category = case_dict["crime_type"]
    
    return {
        "case_id": case_dict["id"],
        "crime_type": case_dict["crime_type"],
        "crime_category": crime_category,
        "latitude": incident_dict.get("latitude") or 0.0,
        "longitude": incident_dict.get("longitude") or 0.0,
        "district": zone_id,
        "police_station": f"{zone_id.replace('-', ' ').title()} Station",
        "incident_time": incident_time,
        "incident_date": incident_date,
        "day_of_week": day_of_week,
        "vehicles": list(vehicles),
        "phones": list(phones),
        "addresses": list(addresses),
        "persons": list(persons),
        "repeat_offender": repeat_offender,
        "weapons": weapons,
        "evidence_tags": evidence_tags,
        "court_outcome": court_outcome,
        "prison_history": prison_history,
        "linked_network_size": linked_cases,
        "risk_zone": zone_id,
        "risk_score": risk_score,
        "hotspot_cluster": hotspot_id,
        "timeline_pattern": timeline_pattern,
        "investigation_stage": "Concluded" if case_dict["status"] == "Closed" else "Ongoing",
        "recommendation_category": "High Priority" if risk_score >= 70 else "Routine Patrol",
    }
