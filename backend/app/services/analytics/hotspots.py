"""DBSCAN geospatial hotspot clustering service."""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
from typing import Any, List, Dict

import numpy as np
from sklearn.cluster import DBSCAN

from .risk import risk_payload
from ...db.models import ZONES
from ...db.repositories import IncidentRepository
from ...utils.helpers import parse_date, iso, NOW


@lru_cache(maxsize=1)
def hotspot_payload() -> List[Dict[str, Any]]:
    """Generate spatial cluster analysis for burglary/theft types using DBSCAN."""
    from datetime import timedelta
    recent = [
        row for row in IncidentRepository.get_incidents_since(iso(NOW - timedelta(days=7)))
        if row["crime_type"] in {"Burglary", "Theft", "Vehicle theft"}
    ]
    
    coordinates = np.array([[row["latitude"], row["longitude"]] for row in recent])
    labels = DBSCAN(eps=0.0038, min_samples=5).fit_predict(coordinates) if len(coordinates) >= 5 else np.array([])
    clusters: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for row, label in zip(recent, labels):
        if label >= 0:
            clusters[int(label)].append(row)
            
    seven_days = IncidentRepository.get_zone_counts(iso(NOW - timedelta(days=7)), iso(NOW), ZONES)
    baseline = IncidentRepository.get_zone_counts(iso(NOW - timedelta(days=14)), iso(NOW - timedelta(days=7)), ZONES)
    risks = {risk["zone_id"]: risk for risk in risk_payload()}
    payload = []
    for zone in ZONES:
        candidates = [items for items in clusters.values() if Counter(item["zone_id"] for item in items).most_common(1)[0][0] == zone["id"]]
        count = sum(len(items) for items in candidates) or seven_days[zone["id"]]
        change = round(((seven_days[zone["id"]] - baseline[zone["id"]]) / max(baseline[zone["id"]], 1)) * 100)
        if count == 0:
            continue
        tone = "critical" if risks[zone["id"]]["score"] >= 80 else "high" if risks[zone["id"]]["score"] >= 65 else "watch"
        payload.append({
            "id": f"cluster-{zone['id']}", "zone_id": zone["id"], "zone_name": zone["name"],
            "incident_count": count, "period_count": seven_days[zone["id"]], "change_percent": change,
            "latitude": zone["lat"], "longitude": zone["lng"], "tone": tone,
            "risk_score": risks[zone["id"]]["score"], "algorithm": "DBSCAN (eps=0.0038, min_samples=5)",
        })
    return sorted(payload, key=lambda item: item["risk_score"], reverse=True)
