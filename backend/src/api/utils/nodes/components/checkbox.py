from pydantic import BaseModel

import api.utils as utils


class Checkbox(BaseModel):
    name = "Checkbox"

    default: bool
