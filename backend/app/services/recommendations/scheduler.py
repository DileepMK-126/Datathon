"""Time-interval scheduler for recommended patrol shifts."""

from __future__ import annotations

from typing import Dict, Any


def schedule_patrol_interval(crime_type: str, night_share: float) -> Dict[str, Any]:
    """Schedule the recommended operational patrol shift window."""
    
    # Scheduling heuristics
    if night_share >= 0.60:
        recommended_shift = "Night Shift (18:00 - 02:00)"
        interval_hours = 8
    elif crime_type.lower() in ["theft", "fraud"]:
        recommended_shift = "Day Shift (08:00 - 16:00)"
        interval_hours = 8
    else:
        recommended_shift = "Evening Shift (14:00 - 22:00)"
        interval_hours = 8
        
    return {
        "recommended_shift": recommended_shift,
        "duration_hours": interval_hours
    }
