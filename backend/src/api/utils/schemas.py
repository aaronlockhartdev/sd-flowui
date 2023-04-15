from typing import Any
from pydantic import BaseModel
import enum


class NodePositionSchema(BaseModel):
    x: int
    y: int


class GraphNodeSchema(BaseModel):
    id: int | None = None
    type: str | None = None
    values: dict[str, Any] | None = None
    position: NodePositionSchema | None = None


class GraphEdgeSchema(BaseModel):
    id: str
    source: int
    sourceHandle: str
    target: int
    targetHandle: str


class GraphQueueSchema(BaseModel):
    id: int | None = None


class GraphUpdateAction(enum.Enum):
    CREATE_NODE = "create_node"
    UPDATE_POSITION_NODE = "update_position_node"
    UPDATE_VALUES_NODE = "update_values_node"
    DELETE_NODE = "delete_node"

    CREATE_EDGE = "create_edge"
    DELETE_EDGE = "delete_edge"

    SYNC_GRAPH = "sync_graph"


class GraphUpdateSchema(BaseModel):
    version: int
    action: GraphUpdateAction
    node: GraphNodeSchema | None = None
    edge: GraphEdgeSchema | None = None
    id: int | None = None

    class Config:
        use_enum_values = True
