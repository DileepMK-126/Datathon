"""NetworkX criminal network, case profiles linkages, alerts, and recommendations services."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from typing import Any, Dict, List

import networkx as nx
from fastapi import HTTPException

from .hotspots import hotspot_payload
from .risk import risk_payload
from .anomaly import trend_payload
from ...db.models import ZONE_INDEX, ZONES
from ...db.repositories import CaseRepository, ZoneRepository
from ...utils.masking import mask_value


@lru_cache(maxsize=16)
def graph_payload(case_id: str | None = None) -> Dict[str, Any]:
    """Build and query a focused shared-identifier criminal association network using NetworkX."""
    case_rows = CaseRepository.get_recent_cases_limit(260)
    entity_rows = CaseRepository.get_all_case_entities()
    
    graph = nx.Graph()
    for row in case_rows:
        graph.add_node(row["id"], kind="case", label=row["id"], zone_id=row["zone_id"], crime_type=row["crime_type"])
    
    valid_cases = {row["id"] for row in case_rows}
    for row in entity_rows:
        if row["case_id"] not in valid_cases:
            continue
        entity_id = f"{row['entity_type']}:{row['normalized_value']}"
        graph.add_node(entity_id, kind=row["entity_type"], label=row["display_value"])
        graph.add_edge(row["case_id"], entity_id, relation=row["entity_type"])
        
    components = [component for component in nx.connected_components(graph) if sum(graph.nodes[node]["kind"] == "case" for node in component) >= 2]
    components.sort(key=len, reverse=True)
    component = next((item for item in components if case_id in item), components[0] if components else set())
    if not component:
        return {"cluster_id": "none", "nodes": [], "edges": [], "summary": "No linked cases were found.", "review_required": True}
        
    focus_case = case_id if case_id in component else next(node for node in component if graph.nodes[node]["kind"] == "case")
    bridge_candidates = [node for node in graph.neighbors(focus_case) if graph.nodes[node]["kind"] in {"phone", "address", "person", "vehicle"}]
    bridge = max(bridge_candidates, key=lambda node: sum(graph.nodes[neighbor]["kind"] == "case" for neighbor in graph.neighbors(node)))
    related_cases = [node for node in graph.neighbors(bridge) if graph.nodes[node]["kind"] == "case" and node != focus_case][:5]
    selected = {focus_case, bridge, *related_cases}
    for related_case in related_cases[:2]:
        for node in graph.neighbors(related_case):
            if graph.nodes[node]["kind"] == "person":
                selected.add(node)
                break
                
    subgraph = graph.subgraph(selected)
    nodes = [
        {"id": node, "kind": attrs["kind"], "label": mask_value(attrs["label"], attrs["kind"]), "zone_id": attrs.get("zone_id"), "crime_type": attrs.get("crime_type")}
        for node, attrs in subgraph.nodes(data=True)
    ]
    edges = [{"source": source, "target": target, "relation": attrs["relation"]} for source, target, attrs in subgraph.edges(data=True)]
    case_count = sum(node["kind"] == "case" for node in nodes)
    return {
        "cluster_id": hashlib.sha1("|".join(sorted(component)).encode()).hexdigest()[:8],
        "nodes": nodes, "edges": edges,
        "summary": f"{case_count} case files connected through repeated synthetic identifiers.",
        "review_required": True,
        "method": "NetworkX shared-entity graph; links are investigative leads only.",
    }


@lru_cache(maxsize=1)
def alerts_payload() -> List[Dict[str, Any]]:
    """Prioritize active operational anomalies, networks, and risk alerts."""
    risks = risk_payload()
    hotspots = hotspot_payload()
    trend = trend_payload("sector-7")
    network = graph_payload()
    top_hotspot = hotspots[0]
    top_risk = risks[0]
    return [
        {
            "id": "anomaly-sector-7", "type": "Anomaly", "level": "critical", "zone_id": "sector-7",
            "title": "Burglary pattern exceeds baseline",
            "text": f"Sector 7 is {trend['change_percent']}% above its expected incident volume over the last 7 days.",
            "confidence": 94, "linked_records": top_hotspot["incident_count"], "detected": "12 min ago",
        },
        {
            "id": "network-cluster", "type": "Network", "level": "high", "zone_id": "old-town",
            "title": "New link found across related cases",
            "text": network["summary"], "confidence": 89, "linked_records": sum(node["kind"] == "case" for node in network["nodes"]), "detected": "34 min ago",
        },
        {
            "id": "risk-window", "type": "Risk", "level": "watch", "zone_id": top_risk["zone_id"],
            "title": "Patrol coverage risk window",
            "text": f"{top_risk['zone_name']} has a {top_risk['label'].lower()} forecast for the next {top_risk['horizon_hours']} hours.",
            "confidence": top_risk["confidence"], "linked_records": 0, "detected": "1 hr ago",
        },
    ]


def unified_case_profile(case_id: str) -> Dict[str, Any]:
    """Retrieve masked and source-attributed records profile for an incident case."""
    case = CaseRepository.get_case_profile(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    sources = CaseRepository.get_case_sources(case_id)
    entities = CaseRepository.get_case_entities(case_id)
    linked = CaseRepository.get_linked_cases(case_id)
    
    return {
        "case": case,
        "sources": sources,
        "entities": [{"type": entity["entity_type"], "label": mask_value(entity["display_value"], entity["entity_type"])} for entity in entities],
        "linked_cases": linked,
        "integration_note": "Records are source-attributed and entity values are masked. Links require analyst validation with the originating system.",
        "human_review_required": True,
    }


def recommendations_payload(zone_id: str) -> Dict[str, Any]:
    """Synthesize evidence-linked suggestions for duty patrols inside a focus zone."""
    if zone_id not in ZONE_INDEX:
        raise HTTPException(status_code=404, detail="Unknown zone")
        
    risk = next(item for item in risk_payload() if item["zone_id"] == zone_id)
    hotspot = next(item for item in hotspot_payload() if item["zone_id"] == zone_id)
    trend = trend_payload(zone_id)
    
    context = ZoneRepository.get_context(zone_id) or {
        "event_factor": "unknown activity", "traffic_index": 0.0
    }
    
    actions = [
        {
            "priority": "Immediate" if risk["score"] >= 80 else "High",
            "action": f"Assign a time-bounded, visible patrol review in {risk['zone_name']} for the next {risk['horizon_hours']} hours.",
            "evidence": f"Risk score {risk['score']}/100; top driver: {risk['drivers'][0]['name']}.",
        },
        {
            "priority": "High",
            "action": "Review the linked-case cluster and validate shared identifiers in the originating systems before opening a joint investigation.",
            "evidence": f"{hotspot['incident_count']} DBSCAN-clustered incidents; trend is {trend['change_percent']}% above baseline.",
        },
        {
            "priority": "Planned",
            "action": "Request a targeted CCTV/evidence review only for the hotspot time window and log the outcome in the case record.",
            "evidence": f"Context: {context['event_factor']} with traffic index {round(context['traffic_index'] * 100)}%.",
        },
    ]
    return {"zone_id": zone_id, "zone_name": risk["zone_name"], "actions": actions, "review_required": True, "automatic_action": False}


def investigation_brief() -> Dict[str, Any]:
    """Establish detect-locate-connect-act operational narrative steps."""
    alert = alerts_payload()[0]
    cluster = hotspot_payload()[0]
    graph = graph_payload()
    focus_case = next((node["id"] for node in graph["nodes"] if node["kind"] == "case"), None)
    recommendations = recommendations_payload(cluster["zone_id"])
    return {
        "headline": alert["title"], "zone_id": cluster["zone_id"], "zone_name": cluster["zone_name"], "focus_case_id": focus_case,
        "steps": [
            {"stage": "Detect", "detail": alert["text"]},
            {"stage": "Locate", "detail": f"DBSCAN identifies {cluster['incident_count']} connected incident records in {cluster['zone_name']}."},
            {"stage": "Connect", "detail": graph["summary"]},
            {"stage": "Act", "detail": recommendations["actions"][0]["action"]},
        ],
        "human_review_required": True,
    }
