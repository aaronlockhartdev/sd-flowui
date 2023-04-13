from fastapi import APIRouter
from pydantic import BaseModel

import api.utils as utils
import api.compute as compute
import api.compute.graph as graph


compute_graph = graph.ComputeGraph()


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
    compute.executor.enqueue(compute_graph, id=queue.id)
