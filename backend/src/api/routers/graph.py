import networkx as nx

from fastapi import APIRouter
from pydantic import BaseModel

from api.utils.nodes import *

graph = nx.DiGraph()
router = APIRouter(prefix="/graph")


class NodeSchema(BaseModel):
    id: int
    type: str
    params: dict


@router.post("/nodes")
async def create_node(node: Node):
    constructor = globals()[node.type]
    graph.add_node(node.id, obj=constructor())


@router.patch("/nodes/{node_id}")
async def update_node(id: int, node: Node):
    graph[id]["obj"].set_params()
