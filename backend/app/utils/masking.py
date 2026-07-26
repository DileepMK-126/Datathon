"""Privacy masking utilities for PII (personally identifiable information)."""

from __future__ import annotations


def mask_value(value: str, kind: str) -> str:
    """Mask sensitive identifier data (phone, address, person name, vehicle) for analysts."""
    if kind == "phone":
        return value[:3] + "•••" + value[-4:]
    if kind == "address":
        return "Address fragment"
    if kind == "person":
        parts = value.split()
        return f"{parts[0][0]}. {parts[-1]}" if len(parts) > 1 else "Named entity"
    if kind == "vehicle":
        return value[:5] + "••••"
    return value
