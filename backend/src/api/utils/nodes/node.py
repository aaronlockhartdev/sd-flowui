from typing import Any
from pydantic import BaseModel, validator

import api.utils as utils


class Connection(BaseModel):
    name: str
    type: type


class Param(BaseModel):
    name: str
    type: type
    default: Any

    @validator("default")
    def default_typematch(default, values):
        if not type(default) is values["type"]:
            raise ValueError(
                f"Invalid default value for variable of type `f{values['type']}`"
            )

        return default


class NodeTemplate(BaseModel):
    inputs: dict[str, Connection] = {}
    outputs: dict[str, Connection] = {}
    params: dict[str, Param]


class Node:
    template: NodeTemplate

    def __init__(self, pos):
        self.pos = pos
        self.params = {k: v.default for k, v in self.template.params.items()}

    @property
    def params(self) -> dict:
        return {k: getattr(self, f"_{k}") for k in self.template.params}

    @params.setter
    def params(self, params: dict):
        for k, v in params.items():
            setattr(self, f"_{k}", v)

    @utils.cached_classproperty
    def component(cls) -> dict:
        component = cls.template.dict()

        for v in component["inputs"].values():
            v["type"] = v["type"].__name__
        for v in component["outputs"].values():
            v["type"] = v["type"].__name__
        for v in component["params"].values():
            v["type"] = v["type"].__name__

        return component
