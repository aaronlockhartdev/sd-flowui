import networkx as nx

from typing import Annotated
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Body
from pydantic import BaseModel, ValidationError, validator

from api.utils.nodes import *
import api.utils.graph as graph_utils

graph = nx.DiGraph()
router = APIRouter(prefix="/graph", tags=["graph"])


class CreateNode(BaseModel):
    id: int
    type: str

    @validator("id")
    def id_dne(cls, id):
        if graph.has_node(id):
            raise ValueError(f"Node `{id}` already exists")

        return id

    @validator("type")
    def type_valid(cls, type):
        if type not in globals():
            raise ValueError(f"Invalid node type `{type}`")

        return type


@router.post("/create_node")
async def create_node(node: CreateNode):
    constructor = globals()[node.type]
    graph.add_node(node.id, obj=constructor())


class UpdateNode(BaseModel):
    id: int
    params: dict

    @validator("id")
    def node_exists(cls, id):
        if not graph.has_node(id):
            raise ValueError(f"Node `{id}` does not exist")

        return id

    @validator("params")
    def kv_valid(cls, params, values):
        id = values["id"]
        for k, v in params.items():
            if k not in graph.nodes[id]["obj"].params:
                raise ValueError(
                    f"Invalid key `{k}` for node of type `{type(graph.nodes[id]['obj']).__name__}`"
                )
            if not isinstance(v, graph.nodes[id]["obj"].params[k]["type"]):
                raise ValueError(
                    f"Invalid type `{type(v).__name__}` for key `{k}` and node of type `{type(graph.nodes[id]['obj']).__name__}`"
                )

        return params


@router.patch("/update_node")
async def update_node(node: UpdateNode):
    graph.nodes[node.id]["obj"].set_params(**node.params)


class DeleteNode(BaseModel):
    id: int

    @validator("id")
    def node_exists(cls, id):
        if not graph.has_node(id):
            raise ValueError(f"Node `{id}` does not exist")

        return id


@router.delete("/delete_node")
async def delete_node(node: DeleteNode):
    graph.remove_node(node.id)


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)
        websocket.send_json(graph_utils.graph_to_json(graph))

    def disconnect(self, websocket: WebSocket):
        self.active.remove(websocket)

    async def update(self, update: dict):
        for websocket in self.active:
            await websocket.send_json(update)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
