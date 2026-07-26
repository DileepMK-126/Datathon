"""Presentation scenario definitions using synthetic indicators."""

from __future__ import annotations

from typing import Dict, Any, List

SCENARIOS: Dict[str, Dict[str, Any]] = {
    "burglary": {
        "id": "burglary",
        "name": "Burglary Investigation Flow",
        "zone_id": "sector-7",
        "case_id": "FIR-7001",
        "description": "Examine nocturnal residential burglary clusters in Sector 7 linked via resolved vehicle entities."
    },
    "vehicle_theft": {
        "id": "vehicle_theft",
        "name": "Vehicle Theft Investigation",
        "zone_id": "old-town",
        "case_id": "FIR-7002",
        "description": "Trace commercial parking garage motorcycle theft hotspots and surveillance overlap."
    },
    "drug_trafficking": {
        "id": "drug_trafficking",
        "name": "Drug Trafficking Network",
        "zone_id": "rivergate",
        "case_id": "FIR-7003",
        "description": "Investigate distribution rings involving communication link graphs and local drug transactions."
    },
    "repeat_offender": {
        "id": "repeat_offender",
        "name": "Repeat Offender Tracking",
        "zone_id": "central",
        "case_id": "FIR-7004",
        "description": "Track high-frequency offenders repeating commercial larceny offenses in Sector 7."
    },
    "gang_network": {
        "id": "gang_network",
        "name": "Gang Network Topology Analysis",
        "zone_id": "sector-7",
        "case_id": "FIR-7001",
        "description": "Map coordinate hierarchies, betweenness centralities, and command structure topologies."
    }
}


def get_all_scenarios() -> List[Dict[str, Any]]:
    """Retrieve lists of available scenarios."""
    return list(SCENARIOS.values())
