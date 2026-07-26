"""Session state container tracking progressive presentation steps."""

from __future__ import annotations

from typing import Dict, Any

# In-memory dictionary tracking demo parameters
_demo_state: Dict[str, Any] = {
    "current_step_index": 0,
    "active_scenario_id": "burglary",
    "timer_mode": "manual",
    "is_playing": False
}


def get_demo_state() -> Dict[str, Any]:
    """Retrieve the current active demo progression state."""
    return _demo_state


def set_demo_step(idx: int) -> None:
    """Set the current step index of the demo."""
    _demo_state["current_step_index"] = idx


def set_demo_scenario(scenario_id: str) -> None:
    """Set the active presentation scenario ID."""
    _demo_state["active_scenario_id"] = scenario_id


def set_demo_play_status(status: bool) -> None:
    """Set whether the auto-play timer is active."""
    _demo_state["is_playing"] = status


def set_demo_timer_mode(mode: str) -> None:
    """Set the auto-play timer duration mode (3min, 5min, manual)."""
    _demo_state["timer_mode"] = mode


def reset_demo_state() -> None:
    """Reset the presentation state parameters."""
    _demo_state["current_step_index"] = 0
    _demo_state["active_scenario_id"] = "burglary"
    _demo_state["timer_mode"] = "manual"
    _demo_state["is_playing"] = False
