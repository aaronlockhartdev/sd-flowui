from pydantic import BaseModel, validator

import api.utils as utils


class Connection(BaseModel):
    id: str
    name: str
    type: type


class Param(BaseModel):
    id: str
    name: str
    component: BaseModel


class NodeTemplate(BaseModel):
    inputs: list[Connection] = []
    outputs: list[Connection] = []
    params: list[Param]


class Node:
    template: NodeTemplate

    def __init__(self, params, pos):
        self.params = params
        self.pos = pos

    @property
    def params(self) -> dict:
        return {p.id: getattr(self, f"_{p.id}") for p in self.template.params}

    @params.setter
    def params(self, params: dict):
        for k, v in params.items():
            setattr(self, f"_{k}", v)

    @utils.cached_classproperty
    def template_computed(cls) -> dict:
        dict = cls.template.dict()

        for c in dict["inputs"] + dict["outputs"]:
            c["type"] = c["type"].__name__

        return dict
