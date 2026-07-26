"""IsolationForest anomaly monitoring service."""

from __future__ import annotations

from datetime import timedelta
from functools import lru_cache
from typing import Any, Dict

import numpy as np
from sklearn.ensemble import IsolationForest

from ...db.repositories import IncidentRepository
from ...utils.helpers import NOW, parse_date, iso


@lru_cache(maxsize=16)
def trend_payload(zone_id: str | None = None, days: int = 28) -> Dict[str, Any]:
    """Train IsolationForest to detect anomalies in crime incident volume over time."""
    rows = IncidentRepository.get_incidents_since(iso(NOW - timedelta(days=days + 7)))
    if zone_id:
        rows = [row for row in rows if row["zone_id"] == zone_id]
    dates = [(NOW - timedelta(days=offset)).date().isoformat() for offset in range(days - 1, -1, -1)]
    counts = []
    for date in dates:
        counts.append(sum(parse_date(row["occurred_at"]).date().isoformat() == date for row in rows))
    baseline_window = counts[: max(7, days // 2)]
    baseline = float(np.mean(baseline_window)) if baseline_window else 0.0
    latest = float(np.mean(counts[-7:])) if counts else 0.0
    change = round((latest - baseline) / max(baseline, 1) * 100)
    features = np.array([[count, index / max(days - 1, 1)] for index, count in enumerate(counts)])
    if len(features) >= 10:
        flags = IsolationForest(contamination=0.12, random_state=11).fit_predict(features)
        anomalies = [dates[index] for index, flag in enumerate(flags) if flag == -1 and index >= days // 2]
    else:
        anomalies = []
    return {
        "zone_id": zone_id, "period_days": days, "labels": dates,
        "actual": counts, "expected": [round(baseline, 1)] * days,
        "baseline": round(baseline, 1), "change_percent": change,
        "anomaly": {"detected": bool(anomalies) or change > 20, "dates": anomalies[-3:], "algorithm": "Isolation Forest + baseline comparison"},
    }
