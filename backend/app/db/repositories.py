"""Repository layer executing SQL queries for cases, incidents, context, and audits."""

from __future__ import annotations

import json
from typing import Any, List, Dict

from .connection import connection
from ..core.database import serialize
from ..utils.helpers import iso


class IncidentRepository:
    @staticmethod
    def get_count() -> int:
        """Get total incident records count."""
        with connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM incidents").fetchone()
        return row["count"] if row else 0

    @staticmethod
    def get_incidents_since(start_iso: str) -> List[Dict[str, Any]]:
        """Get incident records occurred after a specific date."""
        with connection() as conn:
            rows = conn.execute("SELECT * FROM incidents WHERE occurred_at >= ? ORDER BY occurred_at", (start_iso,)).fetchall()
        return [serialize(row) for row in rows]

    @staticmethod
    def get_zone_counts(start_iso: str, end_iso: str, zones_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get counts grouped by zone within a date range."""
        with connection() as conn:
            rows = conn.execute(
                "SELECT zone_id, COUNT(*) AS count FROM incidents WHERE occurred_at >= ? AND occurred_at < ? GROUP BY zone_id",
                (start_iso, end_iso),
            ).fetchall()
        counts = {zone["id"]: 0 for zone in zones_list}
        counts.update({row["zone_id"]: row["count"] for row in rows})
        return counts

    @staticmethod
    def get_geospatial_incidents(min_lng: float, min_lat: float, max_lng: float, max_lat: float, limit: int = 500) -> List[Dict[str, Any]]:
        """Get incidents within bounded box using PostGIS or bounding calculations."""
        with connection() as conn:
            if conn.is_postgres:
                rows = conn.execute(
                    """SELECT id, case_id, zone_id, crime_type, occurred_at, latitude, longitude
                       FROM incidents WHERE geom && ST_MakeEnvelope(?, ?, ?, ?, 4326)
                       ORDER BY occurred_at DESC LIMIT ?""",
                    (min_lng, min_lat, max_lng, max_lat, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT id, case_id, zone_id, crime_type, occurred_at, latitude, longitude
                       FROM incidents WHERE longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?
                       ORDER BY occurred_at DESC LIMIT ?""",
                    (min_lng, max_lng, min_lat, max_lat, limit),
                ).fetchall()
        return [serialize(row) for row in rows]


class CaseRepository:
    @staticmethod
    def get_case_profile(case_id: str) -> Dict[str, Any] | None:
        """Fetch details of a case profile."""
        with connection() as conn:
            case = conn.execute(
                """SELECT cases.id, cases.opened_at, cases.status, cases.summary, cases.crime_type,
                          zones.id AS zone_id, zones.name AS zone_name
                   FROM cases JOIN zones ON zones.id = cases.zone_id WHERE cases.id = ?""",
                (case_id,),
            ).fetchone()
        return serialize(case) if case else None

    @staticmethod
    def get_case_sources(case_id: str) -> List[Dict[str, Any]]:
        """Fetch all source logs related to a case."""
        with connection() as conn:
            sources = conn.execute(
                "SELECT source_system, record_type, recorded_at, payload_json, confidence FROM source_records WHERE case_id = ? ORDER BY recorded_at DESC",
                (case_id,),
            ).fetchall()
        
        items = []
        for src in sources:
            item = serialize(src)
            item["payload"] = json.loads(item.pop("payload_json"))
            items.append(item)
        return items

    @staticmethod
    def get_case_entities(case_id: str) -> List[Dict[str, Any]]:
        """Fetch resolved entities linked to a case."""
        with connection() as conn:
            entities = conn.execute(
                "SELECT entity_type, display_value FROM case_entities WHERE case_id = ? ORDER BY entity_type",
                (case_id,),
            ).fetchall()
        return [serialize(entity) for entity in entities]

    @staticmethod
    def get_linked_cases(case_id: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Find related case linkages based on resolved matching entity values."""
        with connection() as conn:
            linked = conn.execute(
                """SELECT DISTINCT cases.id, cases.crime_type, cases.opened_at, zones.name AS zone_name
                   FROM case_entities focal
                   JOIN case_entities related ON related.normalized_value = focal.normalized_value
                   JOIN cases ON cases.id = related.case_id
                   JOIN zones ON zones.id = cases.zone_id
                   WHERE focal.case_id = ? AND related.case_id != ?
                   ORDER BY cases.opened_at DESC LIMIT ?""",
                (case_id, case_id, limit),
            ).fetchall()
        return [serialize(row) for row in linked]

    @staticmethod
    def get_recent_cases_limit(limit: int = 260) -> List[Dict[str, Any]]:
        """Get the most recent case listings for network graphing."""
        with connection() as conn:
            rows = conn.execute("SELECT * FROM cases ORDER BY opened_at DESC LIMIT ?", (limit,)).fetchall()
        return [serialize(row) for row in rows]

    @staticmethod
    def get_all_case_entities() -> List[Dict[str, Any]]:
        """Get all case entity associations for the graph model."""
        with connection() as conn:
            rows = conn.execute("SELECT * FROM case_entities").fetchall()
        return [serialize(row) for row in rows]

    @staticmethod
    def get_repeat_offender_persons(limit: int = 10) -> List[Dict[str, Any]]:
        """Find person entities that appear in multiple cases."""
        with connection() as conn:
            rows = conn.execute(
                """SELECT entity_type, display_value, COUNT(DISTINCT case_id) AS case_count
                   FROM case_entities WHERE entity_type = 'person'
                   GROUP BY normalized_value HAVING COUNT(DISTINCT case_id) > 1
                   ORDER BY case_count DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        return [serialize(row) for row in rows]


class ZoneRepository:
    @staticmethod
    def get_context(zone_id: str) -> Dict[str, Any] | None:
        """Fetch general geographic context details for a zone."""
        with connection() as conn:
            context = conn.execute("SELECT population_band, traffic_index, event_factor, unemployment_index FROM zone_context WHERE zone_id = ?", (zone_id,)).fetchone()
        return serialize(context) if context else None


class AuditRepository:
    @staticmethod
    def get_audit_logs(limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch system operation audit history logs."""
        with connection() as conn:
            rows = conn.execute("SELECT occurred_at, actor, role, action, resource, outcome, request_id, detail_json FROM audit_events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [serialize(row) for row in rows]
