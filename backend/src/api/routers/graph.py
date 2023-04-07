from __future__ import annotations

import asyncio
import networkx as nx

from fastapi import APIRouter, WebSocket
from pydantic import BaseModel, validator
from typing import Any

import api.services as services
import api.utils as utils
import api.utils.nodes as nodes


class ComputeGraph(nx.DiGraph):
    def __init__(self, *args, **kwargs):
        self.version = 0

        @services.websocket_handler.on_message("graph")
        async def _(data, websocket: WebSocket):
            if data["version"] < self.version:
                await websocket.send(
                    {"stream": "graph", "data": {"action": "sync_graph"}}
                )

                return

            match data["action"]:
                case "create_node":
                    await self.add_node(
                        id=data["id"],
                        type=data["node"]["type"],
                        values=data["node"]["values"],
                        position=data["node"]["position"],
                    )
                case "delete_node":
                    await self.remove_node(id=data["id"])
                case "update_node":
                    await self.update_node(
                        id=data["id"],
                        values=data["node"]["values"],
                        position=data["node"]["position"],
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
            if type(res := func(self, *args, **kwargs)) is list:
                coroutines = []
                for msg in res:
                    self.version += 1

                    msg.update({"version": self.version})
                    coroutines.append(
                        services.websocket_handler.broadcast("graph", msg)
                    )
                await asyncio.gather(*coroutines)

            else:
                self.version += 1

                res.update({"version": self.version})
                await services.websocket_handler.broadcast("graph", res)

        return wrapper

    @_broadcast_update
    def add_node(self, id: int, type: str, values: dict, position: dict) -> dict:
        obj = nodes.constructors[type](values, position)

        super().add_node(id, obj=obj)

        return {"action": "create_node", "node": self._node_to_dict(id).dict()}

    @_broadcast_update
    def update_node(
        self, id: int, values: dict | None = None, position: tuple[int] | None = None
    ) -> dict:
        obj: nodes.Node = self.nodes[id]["obj"]

        msg = {"action": "update_node", "node": {"id": id}}

        if values:
            obj.values = values
            msg["node"].update({"data": {"values": values}})
        if position:
            obj.position = position
            msg["node"].update({"position": {"x": position[0], "y": position[1]}})

        return msg

    @_broadcast_update
    def remove_node(self, id: int) -> dict:
        super().remove_node(id)

        return {"action": "delete_node", "id": id}

    @_broadcast_update
    def add_edge(self, u: int, v: int, map_: dict) -> dict:
        pass

    @_broadcast_update
    def remove_edge(self, u: int, v: int) -> dict:
        pass

    def _node_to_dict(self, id: int) -> utils.NodeSchema:
        obj: nodes.Node = self.nodes[id]["obj"]

        return utils.NodeSchema(
            id=id, type=type(obj).__name__, values=obj.values, position=obj.position
        )

    def _edge_to_list(self, u: int, v: int) -> list[utils.EdgeSchema]:
        map_: dict[str, str] = self.edges[u, v]["map"]

        return [
            utils.EdgeSchema(
                id=f"e{u}{uh}-{v}{vh}",
                source=u,
                sourceHandle=uh,
                target=v,
                targetHandle=vh,
            )
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
