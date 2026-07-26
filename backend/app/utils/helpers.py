"""Common timezone-aware date and helper functions."""

from __future__ import annotations

from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)


def iso(value: datetime) -> str:
    """Format timezone-aware datetime to ISO-8601 string suffixing Z."""
    return value.isoformat().replace("+00:00", "Z")


def parse_date(value: str) -> datetime:
    """Parse ISO-8601 string to timezone-aware datetime."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
