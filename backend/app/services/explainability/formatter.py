"""Formatting and evidence traceability compilers for explanations."""

from __future__ import annotations

from typing import List, Dict, Any
from datetime import timedelta
from ...db.connection import connection
from ...utils.helpers import NOW, iso


def compile_summary(positive: List[Dict[str, Any]], negative: List[Dict[str, Any]]) -> str:
    """Generate a clean, human-readable summary explanation of the risk scoring drivers."""
    if not positive:
        return "The predicted risk is currently within standard baselines and stable patrol coverages."
        
    pos_names = [p["feature"].lower() for p in positive[:2]]
    neg_names = [n["feature"].lower() for n in negative[:2]]
    
    summary = f"The predicted risk is primarily influenced by {', '.join(pos_names)}"
    if neg_names:
        summary += f", and is partially mitigated by {', '.join(neg_names)}."
    else:
        summary += "."
        
    return summary


def trace_evidence(zone_id: str, feature_name: str) -> List[Dict[str, Any]]:
    """Query and trace raw database records representing the evidence for a given feature."""
    with connection() as conn:
        if "volume" in feature_name.lower() or "density" in feature_name.lower() or "burglary" in feature_name.lower():
            # Retrieve recent incidents occurred in the zone over the last 7 days
            rows = conn.execute(
                """SELECT id, case_id, crime_type, occurred_at, latitude, longitude 
                   FROM incidents 
                   WHERE zone_id = ? AND occurred_at >= ? 
                   ORDER BY occurred_at DESC LIMIT 6""",
                (zone_id, iso(NOW - timedelta(days=7)))
            ).fetchall()
            return [
                {
                    "type": "incident",
                    "id": row["id"],
                    "case_id": row["case_id"],
                    "description": f"Incident {row['id']} ({row['crime_type']}) registered at {row['occurred_at']}",
                    "link": f"/api/cases/{row['case_id']}"
                }
                for row in rows
            ]
        elif "patrol" in feature_name.lower() or "gap" in feature_name.lower():
            # Retrieve zone patrol context details
            row = conn.execute(
                "SELECT population_band, unemployment_index, traffic_index FROM zone_context WHERE zone_id = ?",
                (zone_id,)
            ).fetchone()
            if row:
                return [
                    {
                        "type": "context",
                        "id": f"ctx-{zone_id}",
                        "description": f"Population: {row['population_band']}; Unemployment Index: {row['unemployment_index']}; Traffic Index: {round(row['traffic_index']*100)}%",
                        "link": f"/api/recommendations?zone_id={zone_id}"
                    }
                ]
            
    return []
