from pydantic import BaseModel

import transformers


class CLIPModel(BaseModel):
    clip: transformers.CLIPTextModel
    tokenizer: transformers.CLIPTokenizer

    class Config:
        arbitrary_types_allowed = True
