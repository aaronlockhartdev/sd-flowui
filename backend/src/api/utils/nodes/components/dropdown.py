import os
from os import environ as env

from pydantic import BaseModel, Field, validator

import api.utils as utils


class FileDropdown(BaseModel):
    type = Field("FileDropdown", const=True)

    directory: list[str]

    @validator("directory")
    def dir_exists(dir):
        if not os.path.exists(path := os.path.join(env["DATA_DIR"], *dir)):
            # raise ValueError(f"Directory {path} does not exist")
            os.makedirs(path, existok=True)

        return dir
