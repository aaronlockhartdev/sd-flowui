import os
from os import environ as env

from pydantic import BaseModel, Field, validator
from pydantic.main import ModelMetaclass


class ComponentMeta(ModelMetaclass):
    def __new__(cls, name, bases, dict):
        return super().__new__(
            cls, name, bases, {**dict, "type": Field(name, const=True)}
        )


class Component(BaseModel, metaclass=ComponentMeta):
    pass


class Checkbox(Component):
    default: bool


class FileDropdown(Component):
    directory: list[str]

    @validator("directory")
    def dir_exists(dir):
        if not os.path.exists(path := os.path.join(env["DATA_DIR"], *dir)):
            # raise ValueError(f"Directory {path} does not exist")
            os.makedirs(path, exist_ok=True)

        return dir


class FloatSlider(Component):
    default: float
    minimum: float
    maximum: float
    step: float


class TextBox(Component):
    default: str
    placeholder: str
    maxlen: int
    regex: str
