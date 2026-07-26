"""Orchestration engine coordinating SHAP attributions, confidence, and formatting."""

from __future__ import annotations

import time
import logging
from typing import Any, Dict, List
import numpy as np

from .cache import get_cached_explanation, set_cached_explanation
from .shap_engine import calculate_exact_shap
from .confidence import evaluate_confidence
from .formatter import compile_summary, trace_evidence
from ..analytics.risk import get_trained_model_and_features
from ...db.models import ZONE_INDEX, ZONES
from ...db.repositories import IncidentRepository
from ...utils.helpers import NOW, parse_date, iso
from datetime import timedelta

logger = logging.getLogger("sentinel")


def get_risk_explanation(zone_id: str, days: int = 7) -> Dict[str, Any] | None:
    """Orchestrate SHAP-based risk prediction explainability for a zone."""
    start_time = time.perf_counter()
    
    # 1. Check cache first
    cached = get_cached_explanation(zone_id, days)
    if cached is not None:
        logger.info(f"Explainability cache HIT for zone {zone_id}")
        return cached
        
    zone = ZONE_INDEX.get(zone_id)
    if not zone:
        logger.error(f"Zone {zone_id} not found.")
        return None
        
    # 2. Extract feature values for the zone (matching risk_payload)
    model, _, _, feature_names = get_trained_model_and_features()
    
    # Query incidents in this zone within the last 7 days
    rows = IncidentRepository.get_incidents_since(iso(NOW - timedelta(days=days)))
    recent = [row for row in rows if row["zone_id"] == zone_id]
    
    burglary_share = sum(row["crime_type"] == "Burglary" for row in recent) / max(len(recent), 1)
    night_share = sum(parse_date(row["occurred_at"]).hour >= 18 for row in recent) / max(len(recent), 1)
    linked_density = sum(1 for row in recent if int(row["case_id"].split("-")[1]) % 3 == 0) / max(len(recent), 1)
    values = [len(recent) / days, burglary_share, night_share, linked_density, 1 - zone["patrol"]]
    
    # 3. Calculate model probability and score
    probability = float(model.predict_proba([values])[0][1])
    score = round(min(98, max(4, 12 + 5.5 * values[0] + 25 * probability)))
    
    # 4. Calculate SHAP values
    shap_dict = calculate_exact_shap(values)
    
    # 5. Evaluate Confidence
    confidence_data = evaluate_confidence(probability)
    
    # 6. Group drivers by impact direction
    drivers = []
    positive_contributors = []
    negative_contributors = []
    
    for name, shap_val in shap_dict.items():
        impact_percent = int(round(shap_val * 100))
        direction = "positive" if shap_val >= 0 else "negative"
        
        driver = {
            "feature": name,
            "impact": abs(impact_percent),
            "direction": direction,
            "value": round(values[feature_names.index(name)], 2),
            "evidence": trace_evidence(zone_id, name)
        }
        drivers.append(driver)
        
        if direction == "positive":
            positive_contributors.append(driver)
        else:
            negative_contributors.append(driver)
            
    # Sort contributors by absolute impact
    positive_contributors.sort(key=lambda x: x["impact"], reverse=True)
    negative_contributors.sort(key=lambda x: x["impact"], reverse=True)
    
    summary = compile_summary(positive_contributors, negative_contributors)
    
    elapsed = time.perf_counter() - start_time
    logger.info(f"Explainability generated in {elapsed:.4f}s for zone {zone_id}")
    
    response = {
        "zone_id": zone_id,
        "zone_name": zone["name"],
        "risk": score,
        "confidence": confidence_data["score"],
        "confidence_level": confidence_data["level"],
        "confidence_metrics": confidence_data["metrics"],
        "drivers": sorted(drivers, key=lambda x: x["impact"], reverse=True),
        "positive_contributors": positive_contributors,
        "negative_contributors": negative_contributors,
        "summary": summary,
        "execution_time_seconds": round(elapsed, 4)
    }
    
    set_cached_explanation(zone_id, days, response)
    return response
