"""Coordinating engine for guided walkthrough progress control."""

from __future__ import annotations

import logging
from typing import Dict, Any, List

from .state import get_demo_state, set_demo_step, set_demo_scenario, set_demo_play_status, set_demo_timer_mode, reset_demo_state
from .scenarios import SCENARIOS
from .steps import STEPS

logger = logging.getLogger("sentinel")


def start_demo_presentation(scenario_id: str = "burglary", timer_mode: str = "manual") -> Dict[str, Any]:
    """Start or initialize the presentation demonstration session."""
    reset_demo_state()
    
    if scenario_id in SCENARIOS:
        set_demo_scenario(scenario_id)
        
    set_demo_timer_mode(timer_mode)
    set_demo_play_status(True)
    
    logger.info(f"Guided Demo started for scenario {scenario_id} ({timer_mode} mode)")
    return get_current_demo_status()


def progress_next() -> Dict[str, Any]:
    """Step forward to the next walkthrough step index."""
    state = get_demo_state()
    curr = state["current_step_index"]
    
    if curr < len(STEPS) - 1:
        set_demo_step(curr + 1)
        
    return get_current_demo_status()


def progress_previous() -> Dict[str, Any]:
    """Step backward to the previous walkthrough step index."""
    state = get_demo_state()
    curr = state["current_step_index"]
    
    if curr > 0:
        set_demo_step(curr - 1)
        
    return get_current_demo_status()


def get_current_demo_status() -> Dict[str, Any]:
    """Compile the current status, step descriptions, and highlight selectors."""
    state = get_demo_state()
    idx = state["current_step_index"]
    sc_id = state["active_scenario_id"]
    
    step = STEPS[idx]
    scenario = SCENARIOS.get(sc_id, SCENARIOS["burglary"])
    
    return {
        "step_index": idx,
        "total_steps": len(STEPS),
        "step_title": step["title"],
        "highlight_class": step["highlight_class"],
        "directive": step["directive"],
        "narration": step["narration"],
        "scenario_id": sc_id,
        "scenario_name": scenario["name"],
        "target_zone_id": scenario["zone_id"],
        "target_case_id": scenario["case_id"],
        "timer_mode": state["timer_mode"],
        "is_playing": state["is_playing"]
    }
