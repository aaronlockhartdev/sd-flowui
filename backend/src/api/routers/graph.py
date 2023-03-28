import networkx as nx

from typing import Annotated
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Body
from pydantic import BaseModel, ValidationError, validator

import api.utils as utils
import api.utils.nodes as nodes

from api import compute_graph

router = APIRouter(prefix="/graph", tags=["graph"])


class CreateNode(BaseModel):
    id: int
    type: str
    pos: dict[str, int]

    @validator("id")
    def id_dne(cls, id):
        if compute_graph.has_node(id):
            raise ValueError(f"Node `{id}` already exists")

        return id

    @validator("type")
    def type_valid(cls, type):
        if type not in nodes.constructors:
            raise ValueError(f"Invalid node type `{type}`")

        return type


@router.post("/node")
async def create_node(node: CreateNode):
    constructor = nodes.constructors[node.type]

    compute_graph.add_node(node.id, constructor(), pos=node.pos)


class UpdateNode(BaseModel):
    id: int
    params: dict
    pos: dict[str, int]

    @validator("id")
    def node_exists(cls, id):
        if not compute_graph.has_node(id):
            raise ValueError(f"Node `{id}` does not exist")

        return id

    @validator("params")
    def kv_valid(cls, params, values):
        id = values["id"]
        for k, v in params.items():
            if k not in compute_graph.objs[id].params:
                raise ValueError(
                    f"Invalid key `{k}` for node of type `{type(compute_graph.objs[id]).__name__}`"
                )
            if not isinstance(v, compute_graph.objs[id].params[k]["type"]):
                raise ValueError(
                    f"Invalid type `{type(v).__name__}` for key `{k}` and node of type `{type(compute_graph.objs[id]).__name__}`"
                )

        return params


@router.patch("/node")
async def update_node(node: UpdateNode):
    compute_graph.update_node(node.params)


class DeleteNode(BaseModel):
    id: int

    @validator("id")
    def node_exists(cls, id):
        if not compute_graph.has_node(id):
            raise ValueError(f"Node `{id}` does not exist")

        return id


@router.delete("/node")
async def delete_node(node: DeleteNode):
    compute_graph.remove_node(node.id)
