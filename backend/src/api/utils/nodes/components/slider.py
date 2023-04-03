from pydantic import BaseModel


class FloatSlider(BaseModel):
    name = "FloatSlider"

    default: float
    minimum: float
    maximum: float
    step: float
