from pydantic import BaseModel, Field


class FloatSlider(BaseModel):
    type = Field("FloatSlider", const=True)

    default: float
    minimum: float
    maximum: float
    step: float
