"""
MTIC Value Chains API — mirrors the valuechains.ai /api/v1 endpoint shape.

Run:  uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import db
from models import (
    RootsResponse, RootNode, GraphResponse, GraphData,
    GraphNode, GraphRelationship,
)

app = FastAPI(title="MTIC Value Chains API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _node_to_graphnode(n: dict) -> GraphNode:
    props = {k: v for k, v in n.items() if k not in ("id", "label")}
    return GraphNode(id=n["id"], labels=[n["label"]], properties=props)


@app.get("/api/v1/graph/roots", response_model=RootsResponse)
def graph_roots():
    roots = db.get_roots()
    data = [
        RootNode(
            element_id=r["id"], name=r["name"],
            is_public=True, requires_auth=False,
            source_db=r["value_chain_id"],
        )
        for r in roots
    ]
    first = data[0] if data else None
    return RootsResponse(
        data=data,
        message=f"Found {len(data)} accessible root nodes",
        public_value_chain_id=first.element_id if first else None,
        public_value_chain_name=first.name if first else None,
    )


@app.get("/api/v1/graph/incoming/{node_id}", response_model=GraphResponse)
def graph_incoming(
    node_id: str,
    max_iterations: int = Query(4, ge=1, le=30),
    min_threshold: float = Query(0.003, ge=0, le=1),
):
    result = db.get_incoming(node_id, max_iterations, min_threshold)
    if result is None:
        return GraphResponse(success=False, error="Node not found",
                             message=f"No node with id {node_id}")
    data = GraphData(
        nodes=[_node_to_graphnode(n) for n in result["nodes"]],
        relationships=[GraphRelationship(**r) for r in result["relationships"]],
        root_node_id=result["root_node_id"],
        total_nodes=result["total_nodes"],
        total_relationships=result["total_relationships"],
    )
    return GraphResponse(data=data, message="ok")


@app.get("/api/v1/nodes/{node_id}")
def node_detail(node_id: str):
    n = db.get_node(node_id)
    if not n:
        return {"success": False, "error": "Node not found"}
    return {"success": True, "data": n}


@app.get("/api/v1/health")
def health():
    return {"success": True, "status": "ok"}
