from __future__ import annotations

import asyncio
import networkx as nx

from fastapi import APIRouter, WebSocket
from pydantic import BaseModel, validator

import api.services as services
import api.utils.nodes as nodes


class ComputeGraph(nx.DiGraph):
    def __init__(self, *args, **kwargs):
        self.version = 0

        @services.websocket_handler.on_message("graph")
        def _(data, websocket: WebSocket):
            if data["version"] < self.version:
                websocket.send({"stream": "graph", "data": {"action": "sync_graph"}})
                return

            match data["action"]:
                case "create_node":
                    self.add_node(
                        id=data["id"],
                        type=data["node"]["type"],
                        params=data["node"]["params"],
                        pos=data["node"]["pos"],
                    )

        super().__init__(*args, **kwargs)

    @property
    def nodes_computed(self):
        for id in self.nodes:
            yield self._node_to_dict(id)

    @property
    def edges_computed(self):
        for u, v in self.edges:
            yield from self._edge_to_list(u, v)

    @staticmethod
    def _broadcast_update(func):
        async def wrapper(self: ComputeGraph, *args, **kwargs):
            self.version += 1
            if type(res := func(self, *args, **kwargs)) is list:
                await asyncio.gather(
                    *[services.websocket_handler.broadcast("graph", msg) for msg in res]
                )
            else:
                await services.websocket_handler.broadcast("graph", res)

        return wrapper

    @_broadcast_update
    def add_node(self, id: int, type: str, params: dict, pos: tuple[int]) -> dict:
        obj = nodes.constructors[type](params, pos)

        super().add_node(id, obj=obj)

        return {"action": "create_node", "node": self._node_to_dict(id)}

    @_broadcast_update
    def update_node(
        self, id: int, params: dict | None = None, pos: tuple[int] | None = None
    ) -> dict:
        obj: nodes.Node = self.nodes[id]["obj"]

        msg = {"action": "update_node", "node": {"id": id}}

        if params:
            obj.params = params
            msg["element"].update({"data": {"values": params}})
        if pos:
            obj.pos = pos
            msg["element"].update({"position": {"x": pos[0], "y": pos[1]}})

        return msg

    @_broadcast_update
    def remove_node(self, id: int) -> dict:
        super().remove_node(id)

        return {"action": "delete_node", "id": str(id)}

    @_broadcast_update
    def add_edge(self, u: int, v: int, map_: dict) -> dict:
        super().add_edge(u, v, map=map_)

        return [{"action": "create_edge", "edge": e} for e in self._edge_to_list(u, v)]

    @_broadcast_update
    def update_edge(self, u: int, v: int, map_: dict) -> dict:
        actions = [
            {"action": "delete_edge", "id": f"e{u}{uh}-{v}{vh}"}
            for uh, vh in self.edges[u, v]["map"]
        ]

        self.edges[u, v]["map"] = map_

        actions += [
            {"action": "create_edge", "edge": e} for e in self._edge_to_list(u, v)
        ]

        return actions

    @_broadcast_update
    def remove_edge(self, u: int, v: int) -> dict:
        map_ = self.edges[u, v]["map"]
        super().remove_edge()
        return [{"action": "remove_edge", "id": f"e{u}{uh}-{v}{vh}"} for uh, vh in map_]

    def _node_to_dict(self, id: int) -> dict:
        obj: nodes.Node = self.nodes[id]["obj"]

        return {
            "id": str(id),
            "type": "node",
            "data": {
                "label": type(obj).__name__,
                "template": obj.template_computed,
                "values": obj.params,
            },
            "position": {"x": obj.pos[0], "y": obj.pos[1]},
        }

    def _edge_to_list(self, u: int, v: int) -> list[dict]:
        map_: dict[str, str] = self.edges[u, v]["map"]

        return [
            {
                "id": f"e{u}{uh}-{v}{vh}",
                "source": u,
                "sourceHandle": uh,
                "target": v,
                "targetHandle": vh,
            }
            for uh, vh in map_.items()
        ]


compute_graph = ComputeGraph()


router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/")
async def read_graph():
    return {
        "version": compute_graph.version,
        "nodes": list(compute_graph.nodes_computed),
        "edges": list(compute_graph.edges_computed),
        "templates": {k: v.template_computed for k, v in nodes.constructors.items()},
    }


class Position(BaseModel):
    x: int = 0
    y: int = 0


class CreateNode(BaseModel):
    id: int
    type: str
    params: dict
    pos: Position

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
    await compute_graph.add_node(
        node.id, node.type, node.params, (node.pos.x, node.pos.y)
    )


class UpdateNode(BaseModel):
    id: int
    params: dict | None = None
    pos: Position | None = None

    @validator("id")
    def node_exists(cls, id):
        if not compute_graph.has_node(id):
            raise ValueError(f"Node `{id}` does not exist")

        return id


@router.patch("/node")
async def update_node(node: UpdateNode):
    await compute_graph.update_node(params=node.params, pos=(node.pos.x, node.pos.y))


class DeleteNode(BaseModel):
    id: int

    @validator("id")
    def node_exists(cls, id):
        if not compute_graph.has_node(id):
            raise ValueError(f"Node `{id}` does not exist")

        return id


@router.delete("/node")
async def delete_node(node: DeleteNode):
    await compute_graph.remove_node(node.id)
