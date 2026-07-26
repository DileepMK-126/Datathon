"""Orchestration engine coordinating features extraction, matching, and caching."""

from __future__ import annotations

import time
import logging
from typing import Any, Dict, List

from .cache import get_cached_features, set_cached_features, get_cached_similar_cases, set_cached_similar_cases
from .features import extract_features
from .matcher import match_case
from .weights import DEFAULT_WEIGHTS
from ...db.connection import connection

logger = logging.getLogger("sentinel")


def get_similar_cases(
    case_id: str,
    threshold: float = 75.0,
    limit: int = 5,
    weights: Dict[str, float] = DEFAULT_WEIGHTS
) -> Dict[str, Any] | None:
    """Retrieve similar historical cases matching the input case with explainable reasoning."""
    start_time = time.perf_counter()
    
    # 1. Check cache first
    cached_result = get_cached_similar_cases(case_id, threshold, limit)
    if cached_result is not None:
        logger.info(f"Similarity cache HIT for case {case_id}")
        return cached_result
        
    # 2. Extract focal case features
    focal_features = get_cached_features(case_id)
    if not focal_features:
        focal_features = extract_features(case_id)
        if not focal_features:
            logger.error(f"Focal case {case_id} not found in database.")
            return None
        set_cached_features(case_id, focal_features)
        
    # 3. Retrieve all candidate cases (excluding current, deleted, archived)
    # The seeded database cases have statuses like 'Open' or 'Closed'.
    # We will ignore 'deleted' and 'archived' cases (if any cases exist with those statuses).
    with connection() as conn:
        candidates = conn.execute(
            "SELECT id FROM cases WHERE id != ? AND status NOT IN ('deleted', 'archived', 'Deleted', 'Archived')",
            (case_id,)
        ).fetchall()
        
    candidate_ids = [c["id"] for c in candidates]
    
    matches: List[Dict[str, Any]] = []
    rejected_count = 0
    accepted_count = 0
    
    # 4. Compare all candidate cases
    for candidate_id in candidate_ids:
        candidate_features = get_cached_features(candidate_id)
        if not candidate_features:
            candidate_features = extract_features(candidate_id)
            if not candidate_features:
                continue
            set_cached_features(candidate_id, candidate_features)
            
        match_result = match_case(focal_features, candidate_features, weights)
        score = match_result["similarity_score"]
        
        if score >= threshold:
            matches.append(match_result)
            accepted_count += 1
        else:
            rejected_count += 1
            
    # 5. Sort matches by similarity score descending
    matches.sort(key=lambda m: m["similarity_score"], reverse=True)
    
    # Limit to top N matches
    top_matches = matches[:limit]
    
    elapsed = time.perf_counter() - start_time
    logger.info(
        f"Similarity engine completed in {elapsed:.4f}s. "
        f"Candidates: {len(candidate_ids)}, Accepted: {accepted_count}, "
        f"Rejected: {rejected_count}, Threshold: {threshold}%"
    )
    
    response = {
        "case_id": case_id,
        "total_matches": len(top_matches),
        "matches": top_matches,
        "execution_time_seconds": round(elapsed, 4)
    }
    
    # Cache response
    set_cached_similar_cases(case_id, threshold, limit, response)
    
    return response
