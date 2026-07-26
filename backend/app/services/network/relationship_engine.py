"""Relationship explanations and edge descriptions builder."""

from __future__ import annotations

from typing import Dict, Any, List
from .confidence import calculate_relationship_confidence
from ...utils.masking import mask_value


def describe_relationship(source_node: Dict[str, Any], target_node: Dict[str, Any], relation: str) -> Dict[str, Any]:
    """Compile description explaining the edge relationship between two nodes."""
    src_label = mask_value(source_node.get("label", ""), source_node.get("kind", ""))
    tgt_label = mask_value(target_node.get("label", ""), target_node.get("kind", ""))
    
    src_kind = source_node.get("kind", "entity").title()
    tgt_kind = target_node.get("kind", "entity").title()
    
    # Generate reasoning statement
    reason = f"Link establishes connection between {src_kind} ({src_label}) and {tgt_kind} ({tgt_label}) via {relation}."
    
    # Calculate confidence parameters
    confidence = calculate_relationship_confidence(relation)
    
    return {
        "source": source_node["id"],
        "target": target_node["id"],
        "relation": relation,
        "description": reason,
        "confidence": confidence["confidence_score"],
        "explanation": confidence["reason"],
        "supporting_records": confidence["supporting_records"]
    }
