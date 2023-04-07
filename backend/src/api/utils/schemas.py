from typing import Any
from pydantic import BaseModel


class Position(BaseModel):
    x: int
    y: int


class NodeSchema(BaseModel):
    id: int
    type: str
    values: dict[str, Any]
    position: Position


class EdgeSchema(BaseModel):
    id: str
    source: int
    sourceHandle: str
    target: int
    targetHandle: str
