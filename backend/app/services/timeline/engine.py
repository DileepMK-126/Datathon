"""Orchestrator for the timeline generation service, measuring build duration and logging compilation details."""

from __future__ import annotations

import time
from typing import Dict, Any, List

from ...core.logging import logger
from .builder import build_timeline
from .models import TimelineResponseModel, TimelineEventModel


def get_case_timeline(case_id: str) -> Dict[str, Any]:
    """Compile case events, calculate execution duration, log details, and handle failures."""
    start_time = time.perf_counter()
    logger.info("Triggered unified timeline construction for case: %s", case_id)
    
    try:
        events = build_timeline(case_id)
        duration = time.perf_counter() - start_time
        
        # Log missing events alert
        if not events:
            logger.warning("Timeline compiled successfully but returned no events for case: %s", case_id)
        else:
            logger.info(
                "Completed timeline building for case %s in %.4f seconds. Compiled %d events.",
                case_id,
                duration,
                len(events),
            )
            
        return {
            "case_id": case_id,
            "events": [event.model_dump() for event in events]
        }
    except Exception as exc:
        logger.error("Failed to build timeline for case %s: %s", case_id, exc)
        # Re-raise to let the HTTP exception handler format it or return empty
        raise
