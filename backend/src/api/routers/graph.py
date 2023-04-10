from __future__ import annotations

import asyncio
import networkx as nx
import regex as re

from fastapi import APIRouter, WebSocket
from typing import Any

import api.services as services
import api.utils as utils
import api.compute.graph.node as node


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
                    await self.add_node(**data["node"])
                case "delete_node":
                    await self.remove_node(id=data["id"])
                case "update_position_node":
                    await self.update_position_node(
                        data["node"]["id"], data["node"]["position"]
                    )
                case "update_values_node":
                    await self.update_values_node(
                        data["node"]["id"], data["node"]["values"]
                    )
                case "create_edge":
                    await self.add_edge(**data["edge"])
                case "delete_edge":
                    await self.remove_edge(data["id"])

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
        obj = node.nodes[type](values, position)

        super().add_node(id, obj=obj)

        return {"action": "create_node", "node": self._node_to_dict(id).dict()}

    @_broadcast_update
    def update_position_node(self, id: int, position: dict[str, int]) -> dict:
        obj: node.Node = self.nodes[id]["obj"]

        obj.position = position

        return {
            "action": "update_position_node",
            "node": {"id": id, "position": position},
        }

    @_broadcast_update
    def update_values_node(self, id: int, values: dict[str, Any]) -> dict:
        obj: node.Node = self.nodes[id]["obj"]

        obj.values = values

        return {"action": "update_values_node", "node": {"id": id, "values": values}}

    @_broadcast_update
    def remove_node(self, id: int) -> dict:
        super().remove_node(id)

        return {"action": "delete_node", "id": id}

    @_broadcast_update
    def add_edge(
        self, id: str, source: int, target: int, sourceHandle: str, targetHandle: str
    ) -> dict:
        if (source, target) in self.edges:
            self.edges[source, target]["map"].append((sourceHandle, targetHandle))
        else:
            super().add_edge(source, target, map=[(sourceHandle, targetHandle)])

        return {
            "action": "create_edge",
            "edge": {
                "id": id,
                "source": source,
                "target": target,
                "sourceHandle": sourceHandle,
                "targetHandle": targetHandle,
            },
        }

    @_broadcast_update
    def remove_edge(self, id: str) -> dict:
        groups = re.findall("e([1-9]\d*)(\w+)-([1-9]\d*)(\w+)", id)
        u, uh, v, vh = groups

        self.edges[u, v]["map"].remove((uh, vh))
        if not self.edges[u, v]["map"]:
            super().remove_edge(u, v)

        return {"action": "remove_edge", "id": id}

    def _node_to_dict(self, id: int) -> utils.NodeSchema:
        obj: node.Node = self.nodes[id]["obj"]

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
            for uh, vh in map_
        ]


compute_graph = ComputeGraph()


router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/")
async def read_graph():
    return {
        "version": compute_graph.version,
        "nodes": list(compute_graph.nodes_computed),
        "edges": list(compute_graph.edges_computed),
        "templates": {k: v.template_computed for k, v in node.nodes.items()},
    }
