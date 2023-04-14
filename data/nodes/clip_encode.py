import torch
import transformers

from api.compute.graph import Node, NodeTemplate, components


class CLIPEncode(Node):
    _input_text: str

    template = NodeTemplate(
        inputs={"clip": {"name": "CLIP", "type": transformers.CLIPTextModel}},
        outputs={"embeddings": {"name": "CLIP Embeds", "type": torch.FloatTensor}},
        values={
            "input_text": {
                "name": "Text",
                "component": components.TextBox(
                    default="",
                    placeholder="Write your prompt",
                    maxlen=150,
                    regex="(\w+)",
                ),
            }
        },
    )

    def __call__(self, clip):
        pass

    @torch.no_grad()
    def _encode_prompt(self, clip, prompt):
        tokenizer: transformers.CLIPTokenizer = (
            transformers.CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
        )

        text_input = tokenizer(
            prompt,
            padding="max_length",
            max_length=tokenizer.model_max_length,
            truncation=True,
            return_tensors="pt",
        )

        text_embeddings = clip(text_input.input_ids.to())[0]
