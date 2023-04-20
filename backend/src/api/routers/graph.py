from __future__ import annotations

import enum
from typing import Callable, Any, ForwardRef
from pydantic import BaseModel, Field, create_model
from pydantic.main import ModelMetaclass

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
        "templates": {k: v.template.dict() for k, v in graph.node.nodes.items()},
    }


class GraphQueue(BaseModel):
    id: int | None


@router.post("/queue")
async def queue_job(queue: GraphQueue):
    compute.executor.enqueue(compute_graph, id=queue.id)


actions: dict[str, Schema] = {}

Schema = ForwardRef("Schema", is_class=True)


class SchemaMeta(ModelMetaclass):
    def __new__(cls, name, bases, namespace):
        class_ = super().__new__(cls, name, bases, namespace)

        if Schema in bases:
            actions[name[0].lower() + name[1:]] = class_

        return class_


class Schema(BaseModel, metaclass=SchemaMeta):
    _func: Callable

    version: int
    action: str

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True


class CreateNode(Schema):
    _func = "add_node"

    id: int
    type: str
    position: create_model("Position", x=(int, ...), y=(int, ...))
    values: dict[str, Any]


class DeleteNode(Schema):
    _func = "remove_node"

    id: int


class UpdatePositionNode(Schema):
    _func = "update_position_node"

    id: int
    position: create_model("Position", x=(int, ...), y=(int, ...))


class UpdateValuesNode(Schema):
    _func = "update_values_node"

    id: int
    values: dict[str, Any]


class CreateEdge(Schema):
    _func = "add_edge"

    id: str
    source: int
    sourceHandle: str
    target: int
    targetHandle: str


class DeleteEdge(Schema):
    _func = "remove_edge"

    id: str


class GraphUpdate(Schema):
    def __new__(cls, action: str, *args, **kwargs):
        return actions[action](*args, action=action, **kwargs)


@services.websocket_handler.on_message("graph")
@services.websocket_handler.broadcast_func("graph")
def handle_graph_updates(item: GraphUpdate):
    global graph_version

    if item.version != graph_version:
        return {"action": "syncGraph"}

    graph_version += 1
    item.version = graph_version

    compute_graph.__getattribute__(item._func)(
        **{k: v for k, v in item.dict().items() if k not in {"version", "action"}}
    )

    return item
