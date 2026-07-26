"""Graph exporter supporting JSON, CSV, and GraphML formats."""

from __future__ import annotations

import io
import csv
from typing import Dict, Any
import networkx as nx


def export_graph_to_json(graph: nx.Graph) -> Dict[str, Any]:
    """Export NetworkX graph to a custom node-link JSON payload."""
    nodes = []
    for n, attr in graph.nodes(data=True):
        nodes.append({
            "id": n,
            "label": attr.get("label", n),
            "kind": attr.get("kind", "entity"),
            "zone_id": attr.get("zone_id"),
            "centrality": attr.get("centrality", 0.0),
            "community": attr.get("community", 0)
        })
        
    links = []
    for u, v, attr in graph.edges(data=True):
        links.append({
            "source": u,
            "target": v,
            "relation": attr.get("relation", "connected"),
            "confidence": attr.get("confidence", 80)
        })
        
    return {
        "nodes": nodes,
        "links": links
    }


def export_graph_to_graphml(graph: nx.Graph) -> str:
    """Export NetworkX graph as a GraphML formatted string."""
    # Write to a string buffer using NetworkX writer
    buffer = io.BytesIO()
    nx.write_graphml(graph, buffer, encoding="utf-8")
    return buffer.getvalue().decode("utf-8")


def export_graph_to_csv(graph: nx.Graph) -> Dict[str, str]:
    """Export NetworkX graph as separate Nodes and Edges CSV strings."""
    # Nodes CSV
    nodes_buffer = io.StringIO()
    nodes_writer = csv.writer(nodes_buffer)
    nodes_writer.writerow(["id", "label", "kind", "zone_id", "centrality", "community"])
    for n, attr in graph.nodes(data=True):
        nodes_writer.writerow([
            n,
            attr.get("label", n),
            attr.get("kind", "entity"),
            attr.get("zone_id", ""),
            attr.get("centrality", 0.0),
            attr.get("community", 0)
        ])
        
    # Edges CSV
    edges_buffer = io.StringIO()
    edges_writer = csv.writer(edges_buffer)
    edges_writer.writerow(["source", "target", "relation", "confidence"])
    for u, v, attr in graph.edges(data=True):
        edges_writer.writerow([
            u,
            v,
            attr.get("relation", "connected"),
            attr.get("confidence", 80)
        ])
        
    return {
        "nodes_csv": nodes_buffer.getvalue(),
        "edges_csv": edges_buffer.getvalue()
    }
