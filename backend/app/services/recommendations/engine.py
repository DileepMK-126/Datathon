"""Coordinating engine for patrol recommendations generation."""

from __future__ import annotations

import time
import logging
from datetime import timedelta
from typing import Dict, Any, List

from .cache import get_cached_zone_recommendations, set_cached_zone_recommendations
from .rules import evaluate_patrol_rules
from .priority import determine_recommendation_priority
from .scheduler import schedule_patrol_interval
from .impact import estimate_recommendation_impact
from .formatter import compile_recommendation_summary, compile_explanation

from ..analytics.risk import get_trained_model_and_features
from ...db.models import ZONE_INDEX, ZONES
from ...db.repositories import IncidentRepository
from ...utils.helpers import NOW, parse_date, iso

logger = logging.getLogger("sentinel")


def generate_zone_recommendations(zone_id: str) -> List[Dict[str, Any]]:
    """Generate structured, evidence-supported patrol recommendations for a zone."""
    start_time = time.perf_counter()
    
    # 1. Check cache first
    cached = get_cached_zone_recommendations(zone_id)
    if cached is not None:
        logger.info(f"Recommendations cache HIT for zone {zone_id}")
        return cached
        
    zone = ZONE_INDEX.get(zone_id)
    if not zone:
        logger.error(f"Zone {zone_id} not found.")
        return []
        
    # 2. Extract feature values for the zone (matching risk_payload)
    model, _, _, _ = get_trained_model_and_features()
    
    # Query incidents in this zone within the last 7 days
    rows = IncidentRepository.get_incidents_since(iso(NOW - timedelta(days=7)))
    recent = [row for row in rows if row["zone_id"] == zone_id]
    
    burglary_share = sum(row["crime_type"] == "Burglary" for row in recent) / max(len(recent), 1)
    night_share = sum(parse_date(row["occurred_at"]).hour >= 18 for row in recent) / max(len(recent), 1)
    linked_density = sum(1 for row in recent if int(row["case_id"].split("-")[1]) % 3 == 0) / max(len(recent), 1)
    values = [len(recent) / 7.0, burglary_share, night_share, linked_density, 1.0 - zone["patrol"]]
    
    probability = float(model.predict_proba([values])[0][1])
    score = round(min(98, max(4, 12 + 5.5 * values[0] + 25 * probability)))
    
    # Estimate network size (derived from linked density or database)
    network_size = int(len(recent) * linked_density)
    has_hotspot = len(recent) >= 4
    
    # 3. Evaluate Rule Engine
    rule_matches = evaluate_patrol_rules(
        risk_score=score,
        has_hotspot=has_hotspot,
        night_share=night_share,
        patrol_gap=1.0 - zone["patrol"],
        network_size=network_size
    )
    
    # 4. Format recommendation payloads
    recommendations = []
    for idx, match in enumerate(rule_matches):
        category = match["category"]
        
        # Priority and Confidence
        pri_data = determine_recommendation_priority(score, has_hotspot, len(recent) > 3)
        priority = pri_data["priority"]
        confidence = pri_data["confidence"]
        
        # Schedule interval
        sched = schedule_patrol_interval(category, night_share)
        
        # Impact estimation
        impact = estimate_recommendation_impact(category, priority)
        
        # Explanation
        explanation = compile_explanation(category, zone["name"], score, has_hotspot)
        summary = compile_recommendation_summary(category, priority, zone["name"])
        
        recommendations.append({
            "id": f"rec-{zone_id}-{idx+1}",
            "priority": priority,
            "confidence": confidence,
            "category": category,
            "summary": summary,
            "explanation": explanation,
            "recommended_shift": sched["recommended_shift"],
            "duration_hours": sched["duration_hours"],
            "deterrence_level": impact["deterrence_level"],
            "expected_response_reduction": impact["expected_response_reduction"],
            "community_trust_index": impact["community_trust_index"],
            "supporting_evidence": [
                f"Model risk score forecast: {score}%",
                f"Spatial hotspot incident volume: {len(recent)} cases",
                f"Night crime distribution share: {round(night_share*100)}%",
                f"Patrol gap level: {round((1.0 - zone['patrol'])*100)}%"
            ],
            "related_cases": [row["case_id"] for row in recent[:3]],
            "related_hotspots": [f"hotspot-{zone_id}"] if has_hotspot else [],
            "review_required": True
        })
        
    elapsed = time.perf_counter() - start_time
    logger.info(f"Patrol recommendations generated in {elapsed:.4f}s for zone {zone_id}")
    
    set_cached_zone_recommendations(zone_id, recommendations)
    return recommendations
