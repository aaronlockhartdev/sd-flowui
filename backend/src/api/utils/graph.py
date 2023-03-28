import networkx as nx

import api.utils.nodes as nodes

from api import websocket_handler


class ComputeGraph(nx.DiGraph):
    def _node_to_dict(self, id: int, obj: nodes.Node) -> dict:
        return {
            "id": id,
            "type": type(obj).__name__,
            "data": obj.state,
            "position": {"x": obj.pos[0], "y": obj.pos[1]},
        }

    def _edge_to_dict(self, u: int, v: int, map_: dict) -> dict:
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

    @property
    def objs(self):
        return self.nodes.data("obj")

    @property
    def poss(self):
        return self.nodes.data("pos")

    def _broadcast(func):
        def wrapper():
            websocket_handler.broadcast("graph", data := func())
            return data

        return wrapper

    @_broadcast
    def add_node(
        self, id: int, obj: nodes.Node, pos: dict[str, int] | None = None
    ) -> dict:
        super().add_node(id, obj=obj, pos=pos if pos else {"x": 0, "y": 0})

        return {"item": self._node_to_dict(id, obj), "type": "add"}

    @_broadcast
    def update_node(
        self, id: int, params: dict | None, pos: dict[str, int] | None
    ) -> dict:
        obj = self.objs[id]
        obj.params = params
        obj.pos = pos

        return {"update": {"nodes": [self._node_to_dict(id, obj)]}}

    @_broadcast
    def remove_node(self, id: int) -> dict:
        super().remove_node(id)

        return {"id": id, "type": "remove"}

    @_broadcast
    def add_edge(self, u: int, v: int, map_: dict) -> dict:
        super().add_edge(u, v, map=map_)

        return {"create": {"edges": self._edge_to_dict(u, v, map_)}}

    def __iter__(self):
        return {
            [self._node_to_dict(id, self.objs[id]) for id in self.nodes]
            + [self._edge_to_dict(u, v) for u, v in self.edges]
        }
