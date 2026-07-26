"""Pydantic schemas for the Network Intelligence API."""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NetworkNode(BaseModel):
    """Schema representing a single graph node (Entity or Case)."""
    id: str = Field(..., description="Unique node ID")
    label: str = Field(..., description="Masked display label of the node")
    kind: str = Field(..., description="Node category kind (e.g. Person, FIR, Vehicle, Phone, Address)")
    zone_id: Optional[str] = Field(default=None, description="Optional Zone ID reference")
    centrality: float = Field(default=0.0, description="Degree centrality score")
    community: int = Field(default=0, description="Assigned community cluster ID")


class NetworkLink(BaseModel):
    """Schema representing an edge relationship link between nodes."""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relation: str = Field(..., description="Link relationship name")
    confidence: int = Field(..., description="Confidence rating percentage")


class GraphResponse(BaseModel):
    """Custom node-link payload representing the criminal network."""
    nodes: List[NetworkNode]
    links: List[NetworkLink]
    layout: Optional[Dict[str, List[float]]] = Field(default=None, description="Pre-computed coordinate map")


class PathfinderStep(BaseModel):
    """Detailed step description for a connection path link."""
    source: str
    target: str
    relation: str
    description: str
    confidence: int
    explanation: str
    supporting_records: List[str]


class PathfinderResponse(BaseModel):
    """Shortest connection path outcome payload."""
    path: List[str] = Field(..., description="Ordered list of node IDs along the path")
    steps: List[PathfinderStep] = Field(..., description="Attribute explanation details for each connection step")
    length: int = Field(..., description="Total hops/length of the connection path")


class CentralityItem(BaseModel):
    """Attribution item representing node centrality rank."""
    node_id: str
    label: str
    kind: str
    degree_centrality: float
    betweenness_centrality: float


class CommunityCluster(BaseModel):
    """Community list mapping representing network groups."""
    community_id: int
    members: List[NetworkNode]
