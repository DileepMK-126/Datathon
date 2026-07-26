"""Layout positioning algorithms for network graph rendering."""

from __future__ import annotations

from typing import Dict, List, Any
import networkx as nx


def compute_graph_layout(graph: nx.Graph) -> Dict[str, List[float]]:
    """Compute positions for nodes in a graph using NetworkX spring layout, scaled for UI."""
    if len(graph) == 0:
        return {}
        
    # Compute force-directed spring layout
    pos = nx.spring_layout(graph, k=0.35, iterations=40, seed=42)
    
    # Scale positions to fit nice viewport dimensions (e.g. x: 50-750, y: 50-550)
    scaled_positions = {}
    for node, coords in pos.items():
        x = float(coords[0])
        y = float(coords[1])
        
        # Normalize to 50 - 750 (x) and 50 - 450 (y)
        scaled_x = round((x + 1.0) / 2.0 * 700 + 50)
        scaled_y = round((y + 1.0) / 2.0 * 400 + 50)
        
        scaled_positions[str(node)] = [scaled_x, scaled_y]
        
    return scaled_positions
