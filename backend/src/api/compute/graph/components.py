import os
from os import environ as env

from pydantic import BaseModel, Field, validator


class Checkbox(BaseModel):
    type = Field("Checkbox", const=True)

    default: bool


class FileDropdown(BaseModel):
    type = Field("FileDropdown", const=True)

    directory: list[str]

    @validator("directory")
    def dir_exists(dir):
        if not os.path.exists(path := os.path.join(env["DATA_DIR"], *dir)):
            # raise ValueError(f"Directory {path} does not exist")
            os.makedirs(path, exist_ok=True)

        return dir


class FloatSlider(BaseModel):
    type = Field("FloatSlider", const=True)

    default: float
    minimum: float
    maximum: float
    step: float


class TextBox(BaseModel):
    type = Field("TextBox", const=True)

    default: str
    placeholder: str
    maxlen: int
    regex: str
