"""RandomForest risk forecast analysis service."""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from functools import lru_cache
from typing import Any, List, Dict

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from ...db.models import ZONES
from ...db.repositories import IncidentRepository
from ...utils.helpers import NOW, parse_date, iso


@lru_cache(maxsize=1)
def get_trained_model_and_features() -> tuple[Any, List[List[float]], List[int], List[str]]:
    """Train a RandomForestClassifier on rolling synthetic zone-day features and return model context."""
    rows = IncidentRepository.get_incidents_since(iso(NOW - timedelta(days=36)))
    by_zone_day: Dict[tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_zone_day[(row["zone_id"], parse_date(row["occurred_at"]).date().isoformat())].append(row)

    dates = [(NOW - timedelta(days=offset)).date().isoformat() for offset in range(35, -1, -1)]
    features: List[List[float]] = []
    labels: List[int] = []
    feature_names = ["Recent incident volume", "Burglary concentration", "Night-time activity", "Linked-case density", "Patrol coverage gap"]
    global_median = 3.0
    for zone in ZONES:
        for index, date in enumerate(dates[:-1]):
            current = by_zone_day[(zone["id"], date)]
            next_day = by_zone_day[(zone["id"], dates[index + 1])]
            burglary_share = sum(row["crime_type"] == "Burglary" for row in current) / max(len(current), 1)
            night_share = sum(parse_date(row["occurred_at"]).hour >= 18 for row in current) / max(len(current), 1)
            linked_density = sum(1 for row in current if int(row["case_id"].split("-")[1]) % 3 == 0) / max(len(current), 1)
            features.append([len(current), burglary_share, night_share, linked_density, 1 - zone["patrol"]])
            labels.append(int(len(next_day) >= global_median + (1 if zone["id"] in {"sector-7", "old-town"} else 0)))

    model = RandomForestClassifier(n_estimators=160, max_depth=5, min_samples_leaf=2, random_state=17, class_weight="balanced")
    model.fit(features, labels)
    return model, features, labels, feature_names


@lru_cache(maxsize=1)
def risk_payload() -> List[Dict[str, Any]]:
    """Retrieve risks using the trained Random Forest model and calculate attributions."""
    model, X, y, feature_names = get_trained_model_and_features()
    rows = IncidentRepository.get_incidents_since(iso(NOW - timedelta(days=36)))
    output: List[Dict[str, Any]] = []
    for zone in ZONES:
        recent = [row for row in rows if row["zone_id"] == zone["id"] and parse_date(row["occurred_at"]) >= NOW - timedelta(days=7)]
        burglary_share = sum(row["crime_type"] == "Burglary" for row in recent) / max(len(recent), 1)
        night_share = sum(parse_date(row["occurred_at"]).hour >= 18 for row in recent) / max(len(recent), 1)
        linked_density = sum(1 for row in recent if int(row["case_id"].split("-")[1]) % 3 == 0) / max(len(recent), 1)
        values = np.array([len(recent) / 7, burglary_share, night_share, linked_density, 1 - zone["patrol"]], dtype=float)
        baseline = np.array([3.0, 0.30, 0.55, 0.30, 0.40], dtype=float)
        probability = float(model.predict_proba([values])[0][1])
        
        score = round(min(98, max(4, 12 + 5.5 * values[0] + 25 * probability)))
        impacts = model.feature_importances_ * np.maximum(values - baseline, 0)
        if float(impacts.sum()) == 0:
            impacts = model.feature_importances_ * values
        impacts = impacts / impacts.sum() * min(score, 78)
        drivers = [
            {"name": name, "impact": int(round(impact)), "value": round(float(value), 2)}
            for name, impact, value in sorted(zip(feature_names, impacts, values), key=lambda item: item[1], reverse=True)[:3]
        ]
        label = "Critical" if score >= 80 else "High" if score >= 65 else "Elevated" if score >= 45 else "Guarded"
        output.append({
            "zone_id": zone["id"], "zone_name": zone["name"], "score": score, "label": label,
            "confidence": round(max(probability, 0.58) * 100), "horizon_hours": 6,
            "drivers": drivers, "method": "Random Forest local feature attribution",
            "review_required": True,
        })
    return sorted(output, key=lambda item: item["score"], reverse=True)
