from api.utils.nodes.node import Node
import networkx as nx


def graph_to_dict(graph: nx.DiGraph) -> str:
    def node_to_dict(id: int):
        node: Node = graph.nodes[id]["obj"]
        node_dict = {
            "id": id,
            "type": type(node).__name__,
            "params": {k: getattr(node, k) for k in node.params},
        }

        return node_dict

    graph_dict = {
        "nodes": [node_to_dict(n) for n in graph.nodes],
        "edges": [],
    }
