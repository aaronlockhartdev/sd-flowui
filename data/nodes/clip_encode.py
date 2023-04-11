import transformers
import torch

from api.compute.graph import Node, NodeTemplate, components


class CLIPEncode(Node):
    template = NodeTemplate(
        inputs={"clip": {"name": "CLIP", "type": transformers.CLIPTextModel}},
        outputs={"embeddings": {"name": "Embeddings", "type": torch.FloatTensor}},
        values={
            "input_text": {
                "name": "Text",
                "component": components.TextBox(
                    default="", placeholder="Write your prompt", maxlen=150
                ),
            }
        },
    )
