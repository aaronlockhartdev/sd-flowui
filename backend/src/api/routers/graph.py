import networkx as nx

from fastapi import APIRouter
from pydantic import BaseModel

from api.utils.nodes import *

graph = nx.DiGraph()
router = APIRouter(prefix="/graph")


class NodeSchema(BaseModel):
    uid: int
    name: str
    params: str


@router.post("/nodes")
async def create_node(node: Node):
    constructor = globals()[node.name]
    graph.add_node(node.id, obj=constructor())


@router.patch("/nodes/{uid}")
async def update_node(uid: int, node: Node):
    graph[uid]["obj"].set_params()
