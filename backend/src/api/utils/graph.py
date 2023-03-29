import asyncio
import networkx as nx

import api.utils as utils
import api.utils.nodes as nodes


class ComputeGraph(nx.DiGraph):
    def _node_to_dict(self, id: int) -> dict:
        obj = self.objs[id]
        pos = self.poss[id]

        return {
            "id": id,
            "type": type(obj).__name__,
            "data": obj.state,
            "position": {"x": pos[0], "y": pos[1]},
        }

    def _edge_to_dict(self, u: int, v: int, map_: dict[str, str]) -> dict:
        map_ = self.maps[(u, v)]
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
    def objs(self) -> dict[int, nodes.Node]:
        return {k: v for k, v in self.nodes.data("obj")}

    @property
    def poss(self) -> dict[int, tuple[int]]:
        return {k: v for k, v in self.nodes.data("pos")}

    @property
    def maps(self) -> dict[tuple[int], dict[str, str]]:
        return {(u, v): m for u, v, m in self.edges.data("map")}

    def _broadcast(substream: str):
        def decorator(func):
            def wrapper(*args, **kwargs):
                asyncio.create_task(
                    utils.websocket.websocket_handler.broadcast(
                        f"graph/{substream}", data := func(*args, **kwargs)
                    )
                )
                return data

            return wrapper

        return decorator

    @_broadcast("node")
    def add_node(self, id: int, obj: nodes.Node, pos: tuple[int] | None = None) -> dict:
        super().add_node(id, obj=obj, pos=(pos if pos else (0, 0)))

        return {"item": self._node_to_dict(id), "type": "add"}

    @_broadcast("node")
    def update_node(self, id: int, params: dict | None, pos: tuple[int] | None) -> dict:
        obj = self.objs[id]
        if params:
            obj.params = params
        if pos:
            obj.pos = pos

        return {"update": {"nodes": [self._node_to_dict(id)]}}

    @_broadcast("node")
    def remove_node(self, id: int) -> dict:
        super().remove_node(id)

        return {"id": id, "type": "remove"}

    @_broadcast("edge")
    def add_edge(self, u: int, v: int, map_: dict) -> dict:
        super().add_edge(u, v, map=map_)

        return {"create": {"edges": self._edge_to_dict(u, v)}}

    def __iter__(self):
        for id in self.nodes:
            yield self._node_to_dict(id)
        for u, v in self.edges:
            yield from self._edge_to_dict(u, v)


compute_graph = ComputeGraph()
