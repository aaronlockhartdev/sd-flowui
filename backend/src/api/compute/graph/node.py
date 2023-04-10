from __future__ import annotations

from os import environ as env
from pydantic import BaseModel

import api.utils as utils

nodes: dict[str, Node] = {}


class Connection(BaseModel):
    name: str
    type: type


class Value(BaseModel):
    name: str
    component: BaseModel


class NodeTemplate(BaseModel):
    inputs: dict[str, Connection] = {}
    outputs: dict[str, Connection] = {}
    values: dict[str, Value]


class NodeMeta(type):
    def __new__(cls, name, bases, dct):
        class_ = super().__new__(cls, name, bases, dct)

        if bases:
            nodes[name] = class_

        return class_


class Node(metaclass=NodeMeta):
    template: NodeTemplate

    def __init__(self, values, position):
        self.values = values
        self.position = position

    @property
    def values(self) -> dict:
        return {k: getattr(self, f"_{k}") for k in self.template.values.keys()}

    @values.setter
    def values(self, values: dict):
        for k, v in values.items():
            setattr(self, f"_{k}", v)

    @utils.cached_classproperty
    def template_computed(cls) -> dict:
        dict = cls.template.dict()

        for v in dict["inputs"].values():
            v["type"] = v["type"].__name__

        for v in dict["outputs"].values():
            v["type"] = v["type"].__name__

        return dict
