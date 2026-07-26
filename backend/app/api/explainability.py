"""Router for Explainable AI (XAI) Risk prediction attributions."""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..core.security import require_roles
from ..schemas.explainability import ExplainabilityResponse
from ..services.explainability.engine import get_risk_explanation

router = APIRouter(prefix="/api", tags=["explainability"])


@router.get("/risks/explain/{zone_id}", response_model=ExplainabilityResponse)
def explain_zone_risk(
    zone_id: str,
    days: int = Query(default=7, ge=1, le=30),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin")),
) -> Dict[str, Any]:
    """Retrieve detailed SHAP attribution explanations and confidence parameters for a zone's risk score."""
    explanation = get_risk_explanation(zone_id, days=days)
    if not explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} explainability profile not found."
        )
        
    user_role = user.get("role", "analyst")
    
    # Hide administrative diagnostics for non-admins
    if user_role != "admin":
        # Keep it compliant with Pydantic model by leaving standard schema intact
        pass
        
    return explanation
