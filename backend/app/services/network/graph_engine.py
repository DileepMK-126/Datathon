"""Criminal Network Graph compiler and analytics engine."""

from __future__ import annotations

import networkx as nx
from typing import Dict, Any, List, Set
from .cache import get_cached_graph, set_cached_graph
from .confidence import calculate_relationship_confidence
from ...db.repositories import CaseRepository
from ...db.models import ZONES
from ...utils.masking import mask_value

# Node and Edge types constants
NODE_TYPES = [
    "Person", "Vehicle", "Phone", "Address", "FIR", 
    "Court", "Prison", "Evidence", "Organization", 
    "Police Station", "Hotspot", "Investigation"
]

EDGE_TYPES = [
    "Connected To", "Owns", "Registered At", "Called", 
    "Appears In", "Associated With", "Investigated By", 
    "Occurred Near", "Detected By CCTV", "Linked Through Timeline", 
    "Linked Through Similarity"
]


def build_full_network_graph() -> nx.Graph:
    """Compile database entities and cases into a complete NetworkX graph model with centrality and community tags."""
    # 1. Check cache first
    cached = get_cached_graph()
    if cached is not None:
        return cached
        
    G = nx.Graph()
    
    # Load cases
    case_rows = CaseRepository.get_recent_cases_limit(260)
    entity_rows = CaseRepository.get_all_case_entities()
    
    # Set of valid cases
    valid_cases = {row["id"] for row in case_rows}
    
    # 2. Add Case nodes
    for row in case_rows:
        G.add_node(
            row["id"], 
            kind="FIR", # Represent case as FIR type node
            label=row["id"], 
            zone_id=row["zone_id"], 
            crime_type=row["crime_type"]
        )
        
    # 3. Add Entity nodes & ownership / registration edges
    for row in entity_rows:
        if row["case_id"] not in valid_cases:
            continue
            
        entity_kind = row["entity_type"].title()
        entity_id = f"{row['entity_type']}:{row['normalized_value']}"
        
        # Determine appropriate edge connection type
        relation = "Appears In"
        if row["entity_type"] == "person":
            relation = "Associated With"
        elif row["entity_type"] == "vehicle":
            relation = "Owns"
        elif row["entity_type"] == "phone":
            relation = "Called"
        elif row["entity_type"] == "address":
            relation = "Registered At"
            
        # Add entity node if not present
        if entity_id not in G:
            G.add_node(
                entity_id, 
                kind=entity_kind, 
                label=row["display_value"]
            )
            
        # Add edge between case and entity
        confidence = calculate_relationship_confidence(relation)
        G.add_edge(
            row["case_id"], 
            entity_id, 
            relation=relation,
            confidence=confidence["confidence_score"]
        )
        
    # 4. Compute Graph Analytics
    if len(G) > 0:
        # Degree centrality
        deg_centrality = nx.degree_centrality(G)
        
        # Betweenness centrality (approximation or full depending on size)
        between_centrality = nx.betweenness_centrality(G)
        
        # Greedy Modularity Community Detection
        communities = list(nx.community.label_propagation_communities(G))
        community_mapping = {}
        for index, community in enumerate(communities):
            for node in community:
                community_mapping[node] = index
                
        # PageRank
        pagerank = nx.pagerank(G)
        
        # Write analytics parameters into node attributes
        for node in G.nodes():
            G.nodes[node]["centrality"] = float(deg_centrality.get(node, 0.0))
            G.nodes[node]["betweenness"] = float(between_centrality.get(node, 0.0))
            G.nodes[node]["pagerank"] = float(pagerank.get(node, 0.0))
            G.nodes[node]["community"] = community_mapping.get(node, 0)
            
        # Store global graph metrics
        G.graph["density"] = float(nx.density(G))
        G.graph["connected_components"] = int(nx.number_connected_components(G))
            
    set_cached_graph(G)
    return G


def get_subgraph_around_case(case_id: str, radius: int = 1) -> nx.Graph:
    """Extract a local neighborhood ego graph around a selected case ID."""
    G = build_full_network_graph()
    if case_id not in G:
        return nx.Graph()
        
    # Extract ego graph
    ego = nx.ego_graph(G, case_id, radius=radius)
    return ego
