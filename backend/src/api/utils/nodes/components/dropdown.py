import os
from os import environ as env

from pydantic import BaseModel, validator

import api.utils as utils


class FileDropdown(BaseModel):
    name = "FileDropdown"

    directory: str

    @validator("directory")
    def dir_exists(dir):
        if not os.path.exists(path := os.path.join(env["DATA_DIR"], dir)):
            # raise ValueError(f"Directory {path} does not exist")
            os.mkdirs(path, existok=True)

        return dir
