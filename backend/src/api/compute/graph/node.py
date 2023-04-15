from __future__ import annotations

import re
from pydantic import BaseModel, Field, validator

import api.utils as utils

from .components import Component

nodes: dict[str, Node] = {}


class Connection(BaseModel):
    name: str
    type: type = Field(exclude=True)
    typeName: str

    def __init__(self, name: str, type: type):
        super().__init__(name=name, type=type, typeName=type.__name__ if type else "")


class Value(BaseModel):
    name: str
    component: Component


class NodeTemplate(BaseModel):
    inputs: dict[str, Connection] = {}
    outputs: dict[str, Connection] = {}
    values: dict[str, Value]

    @validator("inputs", "outputs", "values")
    def valid_ids(cls, value):
        for k in value.keys():
            if not re.fullmatch("^[a-zA-Z0-9_]+$", k):
                raise ValueError(f"Invalid parameter name '{k}'")

        return value


class NodeMeta(type):
    def __new__(cls, name, bases, dict):
        class_ = super().__new__(cls, name, bases, dict)

        if bases:
            if not "template" in dict:
                raise ValueError("Node must contain a template")

            if not "__call__" in dict:
                raise ValueError("Node must contain a __call__ function")

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
