"""FastAPI router for Similar Case Recommendation Engine."""

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..core.security import require_roles
from ..schemas.similarity import SimilarityResponse
from ..services.similarity.engine import get_similar_cases

router = APIRouter(prefix="/api", tags=["similarity"])


@router.get("/cases/{case_id}/similar", response_model=SimilarityResponse)
def get_similar_cases_endpoint(
    case_id: str,
    limit: int = Query(default=5, ge=1, le=20),
    threshold: float = Query(default=75.0, ge=0.0, le=100.0),
    sort: str = Query(default="score", description="Sort by 'score' or 'date'"),
    category: Optional[str] = Query(default=None, description="Filter matches by crime category"),
    district: Optional[str] = Query(default=None, description="Filter matches by district/zone"),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin")),
) -> Dict[str, Any]:
    """Retrieve similar historical cases with explainable AI reasoning and entity overlap diagnostics."""
    results = get_similar_cases(case_id, threshold=threshold, limit=limit + 10) # Get extra for filtering
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case profile {case_id} not found."
        )
        
    import copy
    matches = results["matches"]
    
    # Filter out current case (already handled in engine, but just in case)
    matches = [m for m in matches if m["case_id"] != case_id]
    
    # Filter by category/crime_type
    if category:
        matches = [m for m in matches if m["crime_type"].lower() == category.lower()]
        
    # Filter by district/zone_id
    if district:
        matches = [m for m in matches if m["details"]["zone_id"].lower() == district.lower()]
        
    # Sort matches
    if sort == "date":
        matches.sort(key=lambda m: m["details"]["incident_date"], reverse=True)
    else: # Default: score
        matches.sort(key=lambda m: m["similarity_score"], reverse=True)
        
    # Slice matches to final limit
    matches = copy.deepcopy(matches[:limit])
    
    # Role-based restriction: Admins get full diagnostics (subscores),
    # supervisors and analysts have empty or masked diagnostics details
    user_role = user.get("role", "analyst")
    for m in matches:
        if user_role != "admin":
            # Mask or remove internal scoring diagnostics if not admin
            m["subscores"] = {}
            
    return {
        "case_id": case_id,
        "total_matches": len(matches),
        "matches": matches,
        "execution_time_seconds": results["execution_time_seconds"]
    }
