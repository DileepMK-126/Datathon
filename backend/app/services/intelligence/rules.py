"""Rule Engine for deterministic threat ranking and confidence assessment."""

from __future__ import annotations

from typing import Dict, Any


def evaluate_priority(risk_score: int, anomaly_detected: bool, cluster_size: int) -> str:
    """Evaluate threat priority level based on risk score, anomalies, and cluster sizes."""
    if risk_score >= 80 and anomaly_detected and cluster_size >= 5:
        return "CRITICAL"
    if risk_score >= 75 and cluster_size >= 5:
        return "HIGH"
    if risk_score >= 65 and (anomaly_detected or cluster_size >= 3):
        return "HIGH"
    if risk_score >= 45 or cluster_size >= 2 or anomaly_detected:
        return "MEDIUM"
    return "LOW"


def calculate_confidence(
    base_confidence: int, 
    anomaly_detected: bool, 
    linked_cases_count: int, 
    hotspot_change: int
) -> int:
    """Combine base model confidence with heuristic signals into a unified rating (capped at 99%)."""
    score = base_confidence
    
    # Anomaly reinforces forecast
    if anomaly_detected:
        score += 8
        
    # Shared criminal entities reinforce lead
    if linked_cases_count >= 3:
        score += 10
    elif linked_cases_count >= 2:
        score += 5
        
    # High cluster surge increases confidence
    if hotspot_change > 50:
        score += 5
    elif hotspot_change < 0:
        score -= 5
        
    return min(99, max(50, score))
