from fastapi import APIRouter
from pydantic import BaseModel, validator

import api.services as services
import api.utils.nodes as nodes

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/elements")
async def read_elements():
    return list(services.compute_graph.elements)


@router.get("/components")
async def read_components():
    return {k: v.template_computed for k, v in nodes.constructors.items()}


class Position(BaseModel):
    x: int = 0
    y: int = 0


class CreateNode(BaseModel):
    id: int
    type: str
    params: dict
    pos: Position

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
    await services.compute_graph.add_node(
        node.id, node.type, node.params, (node.pos.x, node.pos.y)
    )


class UpdateNode(BaseModel):
    id: int
    params: dict | None = None
    pos: Position | None = None

    @validator("id")
    def node_exists(cls, id):
        if not services.compute_graph.has_node(id):
            raise ValueError(f"Node `{id}` does not exist")

        return id


@router.patch("/node")
async def update_node(node: UpdateNode):
    await services.compute_graph.update_node(
        params=node.params, pos=(node.pos.x, node.pos.y)
    )


class DeleteNode(BaseModel):
    id: int

    @validator("id")
    def node_exists(cls, id):
        if not services.compute_graph.has_node(id):
            raise ValueError(f"Node `{id}` does not exist")

        return id


@router.delete("/node")
async def delete_node(node: DeleteNode):
    await services.compute_graph.remove_node(node.id)
