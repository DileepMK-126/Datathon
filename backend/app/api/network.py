"""API router for Criminal Network Intelligence Platform."""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from ..core.security import require_roles
from ..schemas.network import (
    GraphResponse, 
    PathfinderResponse, 
    CentralityItem, 
    CommunityCluster, 
    NetworkNode
)
from ..services.network import (
    build_full_network_graph,
    get_subgraph_around_case,
    find_shortest_path_explanation,
    export_graph_to_json,
    export_graph_to_graphml,
    export_graph_to_csv,
    compute_graph_layout,
    apply_graph_filters
)
from ..utils.masking import mask_value

router = APIRouter(prefix="/api/network", tags=["network"])


@router.get("", response_model=GraphResponse)
def get_network(
    node_types: Optional[List[str]] = Query(default=None),
    edge_types: Optional[List[str]] = Query(default=None),
    zone_ids: Optional[List[str]] = Query(default=None),
    search_query: Optional[str] = Query(default=None),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Retrieve full criminal network graph nodes and links (with optional filters applied)."""
    graph = build_full_network_graph()
    filtered = apply_graph_filters(
        graph, 
        node_types=node_types, 
        edge_types=edge_types, 
        zone_ids=zone_ids, 
        search_query=search_query
    )
    
    # Export to payload format
    payload = export_graph_to_json(filtered)
    
    # Pre-calculate layout
    payload["layout"] = compute_graph_layout(filtered)
    return payload


@router.get("/path", response_model=PathfinderResponse)
def get_connection_path(
    source: str = Query(..., description="ID of source node"),
    target: str = Query(..., description="ID of target node"),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Find the shortest connection path between two criminal entities or cases and describe reasons."""
    graph = build_full_network_graph()
    path_data = find_shortest_path_explanation(graph, source, target)
    if not path_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source or Target node not found in network graph."
        )
    return path_data


@router.get("/centrality", response_model=List[CentralityItem])
def get_node_centralities(
    limit: int = Query(default=30, ge=1),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> List[Dict[str, Any]]:
    """Retrieve top central nodes in the criminal network ranked by Degree Centrality."""
    graph = build_full_network_graph()
    items = []
    for node, attrs in graph.nodes(data=True):
        items.append({
            "node_id": node,
            "label": mask_value(attrs.get("label", node), attrs.get("kind", "")),
            "kind": attrs.get("kind", "entity"),
            "degree_centrality": attrs.get("centrality", 0.0),
            "betweenness_centrality": attrs.get("betweenness", 0.0)
        })
    # Sort by degree centrality descending
    items.sort(key=lambda x: x["degree_centrality"], reverse=True)
    return items[:limit]


@router.get("/community", response_model=List[CommunityCluster])
def get_community_clusters(
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> List[Dict[str, Any]]:
    """Group criminal network nodes into auto-detected community clusters."""
    graph = build_full_network_graph()
    clusters = {}
    for node, attrs in graph.nodes(data=True):
        comm_id = attrs.get("community", 0)
        if comm_id not in clusters:
            clusters[comm_id] = []
            
        clusters[comm_id].append({
            "id": node,
            "label": mask_value(attrs.get("label", node), attrs.get("kind", "")),
            "kind": attrs.get("kind", "entity"),
            "zone_id": attrs.get("zone_id"),
            "centrality": attrs.get("centrality", 0.0),
            "community": comm_id
        })
        
    return [
        {"community_id": cid, "members": members} 
        for cid, members in clusters.items()
    ]


@router.get("/repeat-offenders", response_model=List[NetworkNode])
def get_repeat_offenders_list(
    min_connections: float = Query(default=0.01),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> List[Dict[str, Any]]:
    """Identify highly connected repeat offenders (Person type nodes) in the graph."""
    graph = build_full_network_graph()
    offenders = []
    for node, attrs in graph.nodes(data=True):
        if attrs.get("kind", "").lower() == "person":
            centrality = attrs.get("centrality", 0.0)
            if centrality >= min_connections:
                offenders.append({
                    "id": node,
                    "label": mask_value(attrs.get("label", node), "person"),
                    "kind": "Person",
                    "zone_id": attrs.get("zone_id"),
                    "centrality": centrality,
                    "community": attrs.get("community", 0)
                })
    offenders.sort(key=lambda x: x["centrality"], reverse=True)
    return offenders


@router.get("/export", response_class=Response)
def export_network_file(
    format: str = Query("json", regex="^(json|graphml|csv)$"),
    user: Dict[str, str] = Depends(require_roles("supervisor", "admin"))
) -> Response:
    """Export the network graph configuration files (requires supervisor or admin role)."""
    graph = build_full_network_graph()
    
    if format == "json":
        data = export_graph_to_json(graph)
        import json
        return Response(
            content=json.dumps(data, indent=2), 
            media_type="application/json",
            headers={"Content-Disposition": "attachment;filename=criminal-network.json"}
        )
    elif format == "graphml":
        data = export_graph_to_graphml(graph)
        return Response(
            content=data,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment;filename=criminal-network.graphml"}
        )
    elif format == "csv":
        csvs = export_graph_to_csv(graph)
        # Return nodes CSV as primary
        return Response(
            content=csvs["nodes_csv"],
            media_type="text/csv",
            headers={"Content-Disposition": "attachment;filename=criminal-network-nodes.csv"}
        )
        
    raise HTTPException(status_code=400, detail="Invalid export format.")


@router.get("/{case_id}", response_model=GraphResponse)
def get_local_neighborhood(
    case_id: str,
    radius: int = Query(default=1, ge=1, le=3),
    user: Dict[str, str] = Depends(require_roles("analyst", "supervisor", "admin"))
) -> Dict[str, Any]:
    """Retrieve filtered local ego subgraph around a selected case ID."""
    ego = get_subgraph_around_case(case_id, radius=radius)
    if len(ego) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case ID {case_id} not found in criminal network."
        )
    payload = export_graph_to_json(ego)
    payload["layout"] = compute_graph_layout(ego)
    return payload
