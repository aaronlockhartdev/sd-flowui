import asyncio
import networkx as nx

import api.services as services
import api.utils.nodes as nodes


class ComputeGraph(nx.DiGraph):
    @property
    def elements(self):
        for id in self.nodes:
            yield self._node_to_dict(id)
        for u, v in self.edges:
            yield from self._edge_to_list(u, v)

    @staticmethod
    def _broadcast_update(func):
        async def wrapper(*args, **kwargs):
            if type(res := func(*args, **kwargs)) is list:
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
            msg["node"].update({"data": {"values": params}})
        if pos:
            obj.pos = pos
            msg["node"].update({"position": {"x": pos[0], "y": pos[1]}})

        return msg

    @_broadcast_update
    def remove_node(self, id: int) -> dict:
        super().remove_node(id)

        return {"action": "remove_node", "id": str(id)}

    @_broadcast_update
    def add_edge(self, u: int, v: int, map_: dict) -> dict:
        super().add_edge(u, v, map=map_)

        return [{"action": "create_edge", "edge": e} for e in self._edge_to_list(u, v)]

    @_broadcast_update
    def update_edge(self, u: int, v: int, map_: dict) -> dict:
        actions = [
            {"action": "remove_edge", "id": f"e{u}{uh}-{v}{vh}"}
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
            "label": (name := type(obj).__name__),
            "type": "node",
            "data": {"template": obj.template_computed, "values": obj.params},
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
