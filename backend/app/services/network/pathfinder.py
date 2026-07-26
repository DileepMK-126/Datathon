"""Shortest pathfinder analysis for criminal network graphs."""

from __future__ import annotations

from typing import List, Dict, Any
import networkx as nx
from .relationship_engine import describe_relationship


def find_shortest_path_explanation(graph: nx.Graph, source_id: str, target_id: str) -> Dict[str, Any] | None:
    """Find the shortest path between two nodes in the graph and return explanation details."""
    if source_id not in graph or target_id not in graph:
        return None
        
    try:
        path_nodes = nx.shortest_path(graph, source=source_id, target=target_id)
        
        # Build path steps with relationship explanations
        steps = []
        for i in range(len(path_nodes) - 1):
            u = path_nodes[i]
            v = path_nodes[i + 1]
            edge_data = graph.get_edge_data(u, v)
            relation = edge_data.get("relation", "connected") if edge_data else "connected"
            
            src_node = {"id": u, **graph.nodes[u]}
            tgt_node = {"id": v, **graph.nodes[v]}
            
            steps.append(describe_relationship(src_node, tgt_node, relation))
            
        return {
            "path": path_nodes,
            "steps": steps,
            "length": len(path_nodes) - 1
        }
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return {
            "path": [],
            "steps": [],
            "length": 0,
            "summary": "No connection path exists between the selected nodes."
        }
