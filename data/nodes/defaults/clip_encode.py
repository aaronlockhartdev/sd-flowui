import torch
import transformers

from api.compute.graph import Node, NodeTemplate, components

from .types import CLIPModel


class CLIPEncode(Node):
    _input_text: str

    template = NodeTemplate(
        inputs={"clip": {"name": "CLIP", "type": CLIPModel}},
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
        return self._encode_prompt(clip, self._input_text)

    @torch.no_grad()
    def _encode_prompt(self, clip: transformers.CLIPTextModel, prompt: str):
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

        if (
            hasattr(clip.config, "use_attention_mask")
            and clip.config.use_attention_mask
        ):
            attention_mask = text_input.attention_mask.to()
        else:
            attention_mask = None

        text_embeddings = clip(
            text_input.input_ids.to(), attention_mask=attention_mask
        )[0].to(dtype=clip.dtype)

        return text_embeddings
