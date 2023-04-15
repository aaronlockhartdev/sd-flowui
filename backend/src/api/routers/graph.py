import logging
import logging.config

from fastapi import APIRouter, WebSocket

import api.utils as utils
import api.services as services
import api.compute as compute
import api.compute.graph as graph


compute_graph = graph.ComputeGraph()
graph_version = 1

logging.config.dictConfig(utils.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/")
async def read_graph():
    return {
        "version": graph_version,
        "nodes": list(compute_graph.convert_nodes()),
        "edges": list(compute_graph.convert_edges()),
        "templates": {k: v.template_computed for k, v in graph.node.nodes.items()},
    }


@router.post("/queue")
async def queue_job(queue: utils.GraphQueueSchema):
    print(queue)
    compute.executor.enqueue(compute_graph, id=queue.id)


@services.websocket_handler.on_message("graph")
@services.websocket_handler.broadcast_func("graph")
def handle_graph_updates(data, _: WebSocket):
    global graph_version

    if data["version"] != graph_version:
        return utils.GraphUpdateSchema(action=utils.GraphUpdateAction.SYNC_GRAPH)

    graph_version += 1
    data["version"] = graph_version

    schema = utils.GraphUpdateSchema(**data)

    match data["action"]:
        case utils.GraphUpdateAction.CREATE_NODE.value:
            compute_graph.add_node(**data["node"])

        case utils.GraphUpdateAction.DELETE_NODE.value:
            compute_graph.remove_node(id=data["id"])

        case utils.GraphUpdateAction.UPDATE_POSITION_NODE.value:
            compute_graph.update_position_node(
                data["node"]["id"], data["node"]["position"]
            )

        case utils.GraphUpdateAction.UPDATE_VALUES_NODE.value:
            compute_graph.update_values_node(data["node"]["id"], data["node"]["values"])

        case utils.GraphUpdateAction.CREATE_EDGE.value:
            compute_graph.add_edge(**data["edge"])

        case utils.GraphUpdateAction.DELETE_EDGE.value:
            compute_graph.remove_edge(data["id"])

        case _:
            return utils.GraphUpdateSchema(action=utils.GraphUpdateAction.SYNC_GRAPH)

    return schema
