from __future__ import annotations
from typing import Any

import re
import networkx as nx
from fastapi import WebSocket

import api.utils as utils

from . import node


class ComputeGraph(nx.DiGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_node(self, id: int, type: str, values: dict, position: dict) -> dict:
        obj = node.nodes[type](values, position)

        super().add_node(id, obj=obj)

    def update_position_node(self, id: int, position: dict[str, int]) -> dict:
        obj: node.Node = self.nodes[id]["obj"]

        obj.position = position

    def update_values_node(self, id: int, values: dict[str, Any]) -> dict:
        obj: node.Node = self.nodes[id]["obj"]

        obj.values = values

    def remove_node(self, id: int) -> dict:
        super().remove_node(id)

    def add_edge(
        self, id: str, source: int, target: int, sourceHandle: str, targetHandle: str
    ) -> dict:
        if (source, target) in self.edges:
            self.edges[source, target]["map"].add((sourceHandle, targetHandle))
        else:
            super().add_edge(source, target, map={(sourceHandle, targetHandle)})

    def remove_edge(self, id: str) -> dict:
        u, uh, v, vh = re.findall("e(\d*)(\w+)-(\d*)(\w+)", id)[0]

        u, v = int(u), int(v)

        self.edges[u, v]["map"].remove((uh, vh))
        if not self.edges[u, v]["map"]:
            super().remove_edge(u, v)

    def convert_nodes(self):
        for n in self.nodes:
            yield self.convert_node(n)

    def convert_edges(self):
        for u, v in self.edges:
            yield from self.convert_edge(u, v)

    def convert_node(self, id: int) -> utils.GraphNodeSchema:
        obj: node.Node = self.nodes[id]["obj"]

        return utils.GraphNodeSchema(
            id=id, type=type(obj).__name__, values=obj.values, position=obj.position
        )

    def convert_edge(self, u: int, v: int) -> list[utils.GraphEdgeSchema]:
        map: tuple[str] = self.edges[u, v]["map"]

        return [
            utils.GraphEdgeSchema(
                id=f"e{u}{uh}-{v}{vh}",
                source=u,
                sourceHandle=uh,
                target=v,
                targetHandle=vh,
            )
            for uh, vh in map
        ]
