from pydantic import BaseModel, validator

import api.utils as utils


class Connection(BaseModel):
    name: str
    type: type


class Param(BaseModel):
    name: str
    component: BaseModel


class NodeTemplate(BaseModel):
    inputs: dict[str, Connection] = {}
    outputs: dict[str, Connection] = {}
    values: dict[str, Param]


class Node:
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
