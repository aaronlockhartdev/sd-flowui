from pydantic import BaseModel, Field

import api.utils as utils


class Checkbox(BaseModel):
    type = Field("Checkbox", const=True)

    default: bool
