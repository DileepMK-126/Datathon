"""Filtering rules for network graph exploration."""

from __future__ import annotations

from typing import List, Dict, Any, Set
import networkx as nx


def apply_graph_filters(
    graph: nx.Graph,
    node_types: List[str] | None = None,
    edge_types: List[str] | None = None,
    zone_ids: List[str] | None = None,
    search_query: str | None = None
) -> nx.Graph:
    """Return a subgraph of filtered nodes and edges."""
    filtered = graph.copy()
    
    # Filter nodes by type
    if node_types:
        types_set = {t.lower() for t in node_types}
        nodes_to_remove = [
            n for n, attr in filtered.nodes(data=True) 
            if attr.get("kind", "").lower() not in types_set
        ]
        filtered.remove_nodes_from(nodes_to_remove)
        
    # Filter nodes by zone
    if zone_ids:
        zones_set = {z.lower() for z in zone_ids}
        nodes_to_remove = [
            n for n, attr in filtered.nodes(data=True)
            if attr.get("zone_id") and attr.get("zone_id", "").lower() not in zones_set
        ]
        filtered.remove_nodes_from(nodes_to_remove)
        
    # Filter nodes by search query
    if search_query:
        query = search_query.lower()
        nodes_to_remove = [
            n for n, attr in filtered.nodes(data=True)
            if query not in str(attr.get("label", "")).lower() and query not in str(n).lower()
        ]
        filtered.remove_nodes_from(nodes_to_remove)
        
    # Filter edges by type
    if edge_types:
        etypes_set = {e.lower() for e in edge_types}
        edges_to_remove = [
            (u, v) for u, v, attr in filtered.edges(data=True)
            if attr.get("relation", "").lower() not in etypes_set
        ]
        filtered.remove_edges_from(edges_to_remove)
        
    return filtered
