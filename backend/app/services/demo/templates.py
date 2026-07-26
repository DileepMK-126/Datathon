"""Narration text templates for presentation step narrations."""

from __future__ import annotations

from typing import Dict, Any


def compile_narration_briefing(step_index: int, scenario_name: str) -> str:
    """Generate a descriptive presenter instruction summary for judges."""
    return f"Active Workflow: {scenario_name} (Step {step_index+1}/11). Review AI forecasts and trace links."
