from typing import Any
from pydantic import BaseModel


class NodePositionSchema(BaseModel):
    x: int
    y: int


class GraphNodeSchema(BaseModel):
    id: int
    type: str
    values: dict[str, Any]
    position: NodePositionSchema


class GraphEdgeSchema(BaseModel):
    id: str
    source: int
    sourceHandle: str
    target: int
    targetHandle: str


class GraphQueueSchema(BaseModel):
    id: int | None = None
