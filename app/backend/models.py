"""Pydantic response models mirroring the valuechains.ai API shape."""
from typing import Optional, Any
from pydantic import BaseModel


class RootNode(BaseModel):
    element_id: str
    name: str
    is_public: bool = True
    requires_auth: bool = False
    source_db: str = "mtic"


class RootsResponse(BaseModel):
    success: bool = True
    data: list[RootNode]
    message: str = ""
    public_value_chain_id: Optional[str] = None
    public_value_chain_name: Optional[str] = None


class GraphNode(BaseModel):
    id: str
    labels: list[str]
    properties: dict[str, Any]


class GraphRelationship(BaseModel):
    id: str
    type: str
    start_node_id: str
    end_node_id: str
    properties: dict[str, Any]


class GraphData(BaseModel):
    nodes: list[GraphNode]
    relationships: list[GraphRelationship]
    root_node_id: str
    total_nodes: int
    total_relationships: int


class GraphResponse(BaseModel):
    success: bool = True
    data: Optional[GraphData] = None
    error: Optional[str] = None
    message: str = ""
