from api.compute.graph.node import Node, NodeTemplate

import transformers

import api.utils as utils


class CLIPEncode(Node):
    template = NodeTemplate(
        inputs={"clip": {"name": "CLIP", "type": transformers.CLIPTextModel}},
        outputs={},
        values={
            "input_text": {
                "name": "Text",
                "component": utils.TextBox(
                    default="", placeholder="Write your prompt", maxlen=150
                ),
            }
        },
    )
