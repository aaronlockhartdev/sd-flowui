import asyncio
import networkx as nx

import api.services as services
import api.utils.nodes as nodes


class ComputeGraph(nx.DiGraph):
    def _node_to_dict(self, id: int) -> list[dict]:
        obj: nodes.Node = self.nodes[id]["obj"]

        return [
            {
                "id": str(id),
                "label": (name := type(obj).__name__),
                "type": "input",
                "data": obj.params,
                "position": {"x": obj.pos[0], "y": obj.pos[1]},
            }
        ]

    def _edge_to_dict(self, u: int, v: int) -> list[dict]:
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

    @staticmethod
    def _broadcast_update(func):
        def wrapper(*args, **kwargs):
            asyncio.create_task(
                services.websocket_handler.broadcast(
                    f"graph", msg := func(*args, **kwargs)
                )
            )
            return msg

        return wrapper

    @_broadcast_update
    def add_node(self, id: int, type: str, pos: tuple[int]) -> dict:
        obj = nodes.constructors[type](pos)

        super().add_node(id, obj=obj)

        return {"action": "add", "elements": self._node_to_dict(id)}

    @_broadcast_update
    def update_node(
        self, id: int, params: dict | None = None, pos: tuple[int] | None = None
    ) -> dict:
        obj: nodes.Node = self.nodes[id]["obj"]

        if params:
            obj.params = params
        if pos:
            obj.pos = pos

        return {"action": "update", "elements": self._node_to_dict(id)}

    @_broadcast_update
    def remove_node(self, id: int) -> dict:
        super().remove_node(id)

        return {"action": "remove", "ids": [id]}

    @_broadcast_update
    def add_edge(self, u: int, v: int, map_: dict) -> dict:
        super().add_edge(u, v, map=map_)

        return {"action": "add", "elements": self._edge_to_dict(u, v)}

    @_broadcast_update
    def update_edge(self, u: int, v: int, map_: dict) -> dict:
        self.edges[u, v]["map"] = map_

        return {"action": "update", "elements": self._edge_to_dict(u, v)}

    @_broadcast_update
    def remove_edge(self, u: int, v: int) -> dict:
        map = self.edges[u, v]["map"]
        super().remove_edge()
        return {"action": "remove", "ids": [f"e{u}{uh}-{v}{vh}" for uh, vh in map]}

    def __iter__(self):
        for id in self.nodes:
            yield from self._node_to_dict(id)
        for u, v in self.edges:
            yield from self._edge_to_dict(u, v)


compute_graph = ComputeGraph()
