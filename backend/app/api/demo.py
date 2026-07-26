"""Router for the Guided Presentation Demo Mode."""

from __future__ import annotations

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query

from ..core.security import require_roles
from ..services.demo.engine import start_demo_presentation, progress_next, progress_previous, get_current_demo_status
from ..services.demo.scenarios import get_all_scenarios
from ..services.demo.state import reset_demo_state

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.get("/start")
def get_demo_start(
    scenario: str = Query("burglary"),
    timer: str = Query("manual"),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Start or initialize the presentation demonstration session."""
    return start_demo_presentation(scenario, timer)


@router.get("/next")
def get_demo_next(
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Advance to the next step of the walkthrough progression."""
    return progress_next()


@router.get("/previous")
def get_demo_previous(
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Return to the previous step of the walkthrough progression."""
    return progress_previous()


@router.get("/reset")
def get_demo_reset(
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Reset the demo state parameters."""
    reset_demo_state()
    return get_current_demo_status()


@router.get("/scenarios")
def get_demo_scenarios(
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> List[Dict[str, Any]]:
    """Retrieve lists of available scenarios."""
    return get_all_scenarios()


@router.get("/status")
def get_demo_status(
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Get the current progress step status."""
    return get_current_demo_status()
