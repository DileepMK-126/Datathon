"""Router for evidence-based patrol recommendations and actions."""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..core.security import require_roles
from ..schemas.recommendations import RecommendationResponse, RecommendationItem
from ..services.recommendations.engine import generate_zone_recommendations
from ..db.models import ZONE_INDEX
from ..db.repositories import CaseRepository

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.get("/recommendations", response_model=List[RecommendationItem])
def get_all_recommendations(
    priority: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> List[Dict[str, Any]]:
    """Retrieve all recommendations across zones (with optional priority/category filtering)."""
    all_recs = []
    for zone_id in ZONE_INDEX.keys():
        recs = generate_zone_recommendations(zone_id)
        all_recs.extend(recs)
        
    # Apply filtering
    if priority:
        all_recs = [r for r in all_recs if r["priority"].lower() == priority.lower()]
    if category:
        all_recs = [r for r in all_recs if category.lower() in r["category"].lower()]
        
    return all_recs


@router.get("/recommendations/{zone_id}", response_model=RecommendationResponse)
def get_recommendations_for_zone(
    zone_id: str,
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Retrieve complete evidence-based recommendation list for a specific zone."""
    zone = ZONE_INDEX.get(zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone ID {zone_id} not found."
        )
        
    recs = generate_zone_recommendations(zone_id)
    return {
        "zone_id": zone_id,
        "zone_name": zone["name"],
        "recommendations": recs
    }


@router.get("/recommendations/case/{case_id}", response_model=RecommendationResponse)
def get_recommendations_for_case(
    case_id: str,
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Retrieve recommendations related to the zone where a target case occurred."""
    case = CaseRepository.get_case_profile(case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case ID {case_id} not found."
        )
        
    zone_id = case["zone_id"]
    zone = ZONE_INDEX.get(zone_id)
    recs = generate_zone_recommendations(zone_id)
    
    return {
        "zone_id": zone_id,
        "zone_name": zone["name"] if zone else "Unknown Zone",
        "recommendations": recs
    }


@router.post("/recommendations/{rec_id}/approve")
def approve_recommendation(
    rec_id: str,
    user: Dict[str, str] = Depends(require_roles("supervisor", "admin"))
) -> Dict[str, Any]:
    """Approve a recommendation for operational dispatch (requires supervisor or admin role)."""
    return {
        "recommendation_id": rec_id,
        "approved": True,
        "approver": user.get("username", "system-supervisor"),
        "status": "Operational Dispatch Pending"
    }


@router.get("/investigations/brief")
def get_investigation_story(
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Retrieve detect-locate-connect-act brief narrative steps."""
    from ..services.analytics.network import investigation_brief
    return investigation_brief()
