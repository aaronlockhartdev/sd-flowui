import asyncio
import networkx as nx

import api.utils as utils
import api.utils.nodes as nodes


def broadcast_update(func):
    def wrapper(*args, **kwargs):
        asyncio.create_task(
            utils.websocket.websocket_handler.broadcast(
                f"graph", msg := func(*args, **kwargs)
            )
        )
        return msg

    return wrapper


class ComputeGraph(nx.DiGraph):
    def _node_to_dict(self, id: int) -> list[dict]:
        obj: nodes.Node = self.nodes[id]["obj"]
        pos: tuple[int] = self.nodes[id]["pos"]

        return [
            {
                "id": id,
                "type": type(obj).__name__,
                "data": obj.state,
                "position": {"x": pos[0], "y": pos[1]},
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

    @broadcast_update
    def add_node(self, id: int, obj: nodes.Node, pos: tuple[int] | None = None) -> dict:
        super().add_node(id, obj=obj, pos=(pos if pos else (0, 0)))

        return {"action": "add", "elements": self._node_to_dict(id)}

    @broadcast_update
    def update_node(self, id: int, params: dict | None, pos: tuple[int] | None) -> dict:
        if params:
            self.nodes[id]["obj"].params = params
        if pos:
            self.nodes[id]["pos"] = pos

        return {"action": "update", "elements": self._node_to_dict(id)}

    @broadcast_update
    def remove_node(self, id: int) -> dict:
        super().remove_node(id)

        return {"action": "remove", "ids": [id]}

    @broadcast_update
    def add_edge(self, u: int, v: int, map_: dict) -> dict:
        super().add_edge(u, v, map=map_)

        return {"action": "add", "elements": self._edge_to_dict(u, v)}

    @broadcast_update
    def update_edge(self, u: int, v: int, map_: dict) -> dict:
        self.edges[u, v]["map"] = map_

        return {"action": "update", "elements": self._edge_to_dict(u, v)}

    @broadcast_update
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
