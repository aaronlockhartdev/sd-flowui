import networkx as nx

import api.utils.nodes as nodes

from api import websocket_handler


def broadcast(func):
    def wrapper():
        websocket_handler.broadcast("graph", data := func())
        return data

    return wrapper


class Graph(nx.DiGraph):
    def _node_to_dict(self, id: int, obj: nodes.Node):
        return {
            "id": id,
            "type": type(obj).__name__,
            "params": {k: getattr(obj, k) for k in obj.params},
        }

    def _edge_to_dict(self, u: int, v: int, mapping: dict):
        return [
            {"u": {"node": u, "handle": uh}, "v": {"node": v, "handle": vh}}
            for uh, vh in mapping.items
        ]

    @websocket_handler.on_connect("graph")
    def to_dict(self) -> dict:
        return {
            "create": {
                "nodes": [
                    self._node_to_dict(id, obj) for id, obj in self.nodes.data("obj")
                ],
                "edges": [
                    self._edge_to_dict(u, v, mapping)
                    for u, v, mapping in self.nodes.data("order")
                ],
            }
        }

    @broadcast
    def add_node(self, id: int, obj: nodes.Node = None):
        super().add_node(id, obj=obj)

        return {"create": {"nodes": [self._node_to_dict(id, obj)]}}

    @broadcast
    def add_edge(self, u: int, v: int, mapping: dict):
        super().add_edge(u, v, mapping=mapping)

        return {"create": {"edges": self._edge_to_dict(u, v, mapping)}}

    @broadcast
    def remove_node(self, id: int):
        super().remove_node(id)

        return {"delete": {"nodes": {"id": id}}}
