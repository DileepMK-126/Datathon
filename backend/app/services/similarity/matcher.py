"""Matching rules and reasoning compiler for Sentinel's similar case engine."""

from __future__ import annotations

from typing import Any, Dict, List
from .scoring import jaccard_similarity, geospatial_similarity, temporal_similarity, cosine_similarity_flat
from .weights import DEFAULT_WEIGHTS
from ...utils.masking import mask_value


def compile_reasoning(case_type: str, geo_score: float, matched_entities: Dict[str, List[str]], hotspot_match: bool, time_score: float) -> str:
    """Generate human-readable, explainable reasoning details for a case match."""
    reasons = []
    
    # Crime Type reason
    reasons.append(f"involve the same crime type ({case_type.lower()})")
    
    # Location/Hotspot reason
    if hotspot_match:
        reasons.append("belong to the same hotspot cluster")
    elif geo_score > 0.8:
        reasons.append("occurred in extremely close proximity (within 1-2 km)")
    elif geo_score > 0.6:
        reasons.append("occurred in the same general sector/area")
        
    # Shared entities reasons
    for etype, vals in matched_entities.items():
        if vals:
            masked_vals = [mask_value(v, etype) for v in vals[:2]]
            suffix = "s" if len(vals) > 1 else ""
            reasons.append(f"share {len(vals)} {etype} identifier{suffix} ({', '.join(masked_vals)})")
            
    # Temporal reason
    if time_score > 0.8:
        reasons.append("occurred within a very close time window")
        
    if not reasons:
        return "Matched based on general demographic and risk attributes."
        
    # Combine reasons smoothly
    if len(reasons) == 1:
        return f"Both investigations {reasons[0]}."
    elif len(reasons) == 2:
        return f"Both investigations {reasons[0]} and {reasons[1]}."
    else:
        return f"Both investigations {', '.join(reasons[:-1])}, and {reasons[-1]}."


def match_case(f1: Dict[str, Any], f2: Dict[str, Any], weights: Dict[str, float] = DEFAULT_WEIGHTS) -> Dict[str, Any]:
    """Compare two case feature profiles and return subscores and composite similarity score."""
    
    # 1. Crime Type Similarity (25% default)
    crime_type_score = 1.0 if f1["crime_type"] == f2["crime_type"] else 0.0
    
    # 2. Location Similarity (20% default)
    loc_score = geospatial_similarity(f1["latitude"], f1["longitude"], f2["latitude"], f2["longitude"])
    
    # 3. Entity Overlap (20% default)
    entities1 = set(f1["phones"] + f1["vehicles"] + f1["addresses"] + f1["persons"])
    entities2 = set(f2["phones"] + f2["vehicles"] + f2["addresses"] + f2["persons"])
    entity_score = jaccard_similarity(entities1, entities2)
    
    # 4. Timeline Similarity (10% default)
    timeline_score = temporal_similarity(
        f1["incident_date"] + "T" + f1["incident_time"],
        f2["incident_date"] + "T" + f2["incident_time"]
    )
    
    # 5. Network Similarity (10% default)
    network_diff = abs(f1["linked_network_size"] - f2["linked_network_size"])
    max_network = max(f1["linked_network_size"], f2["linked_network_size"], 1)
    network_score = 1.0 - (network_diff / max_network)
    
    # 6. Vehicle Similarity (5% default)
    veh_score = jaccard_similarity(set(f1["vehicles"]), set(f2["vehicles"]))
    
    # 7. Phone Similarity (5% default)
    phone_score = jaccard_similarity(set(f1["phones"]), set(f2["phones"]))
    
    # 8. Risk Zone Similarity (5% default)
    risk_score = 1.0 if f1["risk_zone"] == f2["risk_zone"] else 0.0
    
    # Calculate composite score
    subscores = {
        "crime_type": crime_type_score,
        "location": loc_score,
        "entity_match": entity_score,
        "timeline": timeline_score,
        "network": network_score,
        "vehicle": veh_score,
        "phone": phone_score,
        "risk_zone": risk_score,
    }
    
    total_score = sum(subscores[k] * weights.get(k, 0.0) for k in subscores)
    
    # Calculate shared entities for explanation
    shared_entities = {
        "phone": list(set(f1["phones"]).intersection(set(f2["phones"]))),
        "vehicle": list(set(f1["vehicles"]).intersection(set(f2["vehicles"]))),
        "person": list(set(f1["persons"]).intersection(set(f2["persons"]))),
        "address": list(set(f1["addresses"]).intersection(set(f2["addresses"]))),
    }
    
    hotspot_match = f1["hotspot_cluster"] != "none" and f1["hotspot_cluster"] == f2["hotspot_cluster"]
    reasoning = compile_reasoning(
        f1["crime_type"],
        loc_score,
        shared_entities,
        hotspot_match,
        timeline_score
    )
    
    confidence = "Critical Match" if total_score >= 0.90 else "Strong Match" if total_score >= 0.80 else "Moderate Match" if total_score >= 0.70 else "Weak Match"
    
    return {
        "case_id": f2["case_id"],
        "crime_type": f2["crime_type"],
        "similarity_score": round(total_score * 100, 1),
        "confidence": confidence,
        "subscores": subscores,
        "reasoning": reasoning,
        "shared_entities": {
            "phones": [mask_value(p, "phone") for p in shared_entities["phone"]],
            "vehicles": [mask_value(v, "vehicle") for v in shared_entities["vehicle"]],
            "persons": [mask_value(pe, "person") for pe in shared_entities["person"]],
            "addresses": [mask_value(a, "address") for a in shared_entities["address"]],
        },
        "details": f2
    }
