import networkx as nx

from fastapi import APIRouter
from pydantic import BaseModel, validator

import api.utils as utils
import api.services as services
import api.utils.nodes as nodes

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/")
async def read_graph():
    return list(services.compute_graph)


@router.get("/components")
async def read_components():
    return [v.component for v in nodes.constructors.values()]


class CreateNode(BaseModel):
    id: int
    type: str
    posx: int
    posy: int

    @validator("id")
    def id_dne(cls, id):
        if services.compute_graph.has_node(id):
            raise ValueError(f"Node `{id}` already exists")

        return id

    @validator("type")
    def type_valid(cls, type):
        if type not in nodes.constructors:
            raise ValueError(f"Invalid node type `{type}`")

        return type


@router.post("/node")
async def create_node(node: CreateNode):
    return services.compute_graph.add_node(
        node.id, node.type, pos=(node.posx, node.posy)
    )


class UpdateNode(BaseModel):
    id: int
    params: dict
    posx: int
    posy: int

    @validator("id")
    def node_exists(cls, id):
        if not services.compute_graph.has_node(id):
            raise ValueError(f"Node `{id}` does not exist")

        return id

    @validator("params")
    def kv_valid(cls, params, values):
        id = values["id"]
        for k, v in params.items():
            obj: nodes.Node = services.compute_graph.nodes[id]["obj"]
            if k not in obj.params:
                raise ValueError(
                    f"Invalid key `{k}` for node of type `{type(obj).__name__}`"
                )
            if not isinstance(v, obj.params[k]["type"]):
                raise ValueError(
                    f"Invalid type `{type(v).__name__}` for key `{k}` and node of type `{type(obj).__name__}`"
                )

        return params


@router.patch("/node")
async def update_node(node: UpdateNode):
    return services.compute_graph.update_node(node.params, pos=(node.posx, node.posy))


class DeleteNode(BaseModel):
    id: int

    @validator("id")
    def node_exists(cls, id):
        if not services.compute_graph.has_node(id):
            raise ValueError(f"Node `{id}` does not exist")

        return id


@router.delete("/node")
async def delete_node(node: DeleteNode):
    return services.compute_graph.remove_node(node.id)
