"""Deterministic summary text templates for the Intelligence Engine."""

from __future__ import annotations


def get_hotspot_text(zone_name: str, crime_type: str, count: int, change: int) -> str:
    """Format hotspot summary template based on cluster size and baseline deviation."""
    direction = "increase" if change >= 0 else "decrease"
    change_abs = abs(change)
    return (
        f"{zone_name} has experienced an unusual {direction} in {crime_type.lower()} incidents during recent intervals. "
        f"The hotspot model identified a dense cluster containing {count} active incidents, representing a {change_abs}% deviation against historical baselines."
    )


def get_trend_text(anomaly_detected: bool, baseline: float, period_days: int) -> str:
    """Format anomaly summary template based on Isolation Forest outputs."""
    if anomaly_detected:
        return (
            f"The anomaly detection model flagged a statistically significant volume escalation. "
            f"Isolation Forest scans detected a baseline breach above the expected average of {baseline:.1f} reports over the previous {period_days}-day period."
        )
    return f"Time-series monitoring indicates volume remains within normal statistical limits relative to the expected average of {baseline:.1f} reports."


def get_network_text(case_count: int, entities_count: int) -> str:
    """Format network summary template based on NetworkX resolved nodes."""
    if case_count >= 2:
        return (
            f"Entity-resolution graph mapping linked {case_count} active investigations that share repeated identifiers "
            f"({entities_count} resolved phone, vehicle, address, or name coordinates in the network)."
        )
    return "Entity resolution graph analysis detected no persistent shared identifier links to other active case profiles."


def get_risk_text(score: int, label: str, horizon: int, top_driver: str) -> str:
    """Format explainable area risk template based on Random Forest classifier outputs."""
    return (
        f"Forecasting models score this sector at {score}/100, indicating a {label.lower()} risk rating for the next {horizon} hours. "
        f"The primary calculated feature-attribution driver is '{top_driver}'."
    )


def assemble_investigation_summary(hotspot_txt: str, network_txt: str, trend_txt: str, risk_txt: str) -> str:
    """Combine structured component texts into a unified summary paragraph."""
    return f"{hotspot_txt}\n\n{network_txt}\n\n{trend_txt} {risk_txt}"
