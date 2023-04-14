import logging
import logging.config

from fastapi import APIRouter, WebSocket

import api.utils as utils
import api.services as services
import api.compute as compute
import api.compute.graph as graph


compute_graph = graph.ComputeGraph()

logging.config.dictConfig(utils.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/")
async def read_graph():
    return {
        "version": compute_graph.version,
        "nodes": list(compute_graph.nodes_computed),
        "edges": list(compute_graph.edges_computed),
        "templates": {k: v.template_computed for k, v in graph.node.nodes.items()},
    }


@router.post("/queue")
async def queue_job(queue: utils.GraphQueueSchema):
    print(queue)
    compute.executor.enqueue(compute_graph, id=queue.id)


@services.websocket_handler.on_message("graph")
async def handle_graph_updates(data, websocket: WebSocket):
    if data["version"] < compute_graph.version:
        await websocket.send({"stream": "graph", "data": {"action": "sync_graph"}})

        return

    match data["action"]:
        case "create_node":
            await compute_graph.add_node(**data["node"])
        case "delete_node":
            await compute_graph.remove_node(id=data["id"])
        case "update_position_node":
            await compute_graph.update_position_node(
                data["node"]["id"], data["node"]["position"]
            )
        case "update_values_node":
            await compute_graph.update_values_node(
                data["node"]["id"], data["node"]["values"]
            )
        case "create_edge":
            await compute_graph.add_edge(**data["edge"])
        case "delete_edge":
            await compute_graph.remove_edge(data["id"])
