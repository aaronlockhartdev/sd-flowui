import os
import yaml
import pathlib
from os import environ as env

import torch
import safetensors
import diffusers, transformers
from diffusers.pipelines.stable_diffusion.convert_from_ckpt import (
    create_unet_diffusers_config,
    convert_ldm_unet_checkpoint,
    create_vae_diffusers_config,
    convert_ldm_vae_checkpoint,
    convert_open_clip_checkpoint,
    convert_ldm_clip_checkpoint,
)

import api.utils as utils
from api.compute.graph import Node, NodeTemplate, components


class LoadCheckpoint(Node):
    _ckpt_path: list[str]
    _cfg_path: list[str]
    _upcast_att: bool
    _use_ema: bool
    _size_768: bool

    template = NodeTemplate(
        values={
            "ckpt_path": {
                "name": "Checkpoint",
                "component": components.FileDropdown(directory=["checkpoints"]),
            },
            "cfg_path": {
                "name": "Config",
                "component": components.FileDropdown(directory=["configs"]),
            },
            "upcast_att": {
                "name": "Upcast Attention",
                "component": components.Checkbox(default=True),
            },
            "use_ema": {
                "name": "Use EMA",
                "component": components.Checkbox(default=True),
            },
            "size_768": {
                "name": "768 Model",
                "component": components.Checkbox(default=True),
            },
        },
        outputs={
            "clip": {"name": "CLIP", "type": transformers.CLIPTextModel},
            "unet": {"name": "UNet", "type": diffusers.UNet2DConditionModel},
            "vae": {"name": "VAE", "type": diffusers.AutoencoderKL},
        },
    )

    def __call__(self):
        config_path = os.path.join(env["DATA_DIR"], "configs", *self._cfg_path)
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        ckpt_path = os.path.join(
            env["DATA_DIR"], "models", "checkpoints", *self._ckpt_path
        )
        if pathlib.Path(ckpt_path).suffix == "safetensors":
            ckpt = {}
            with safetensors.safe_open(ckpt_path, framework="pt", device="cpu") as f:
                for key in f.keys():
                    ckpt[key] = f.get_tensor(key)
        else:
            ckpt = torch.load(ckpt_path)

        return {
            "unet": self._load_unet(ckpt, config),
            "vae": self._load_vae(ckpt, config),
            "clip": self._load_clip(ckpt, config),
        }

    def _load_unet(self, ckpt, config) -> diffusers.UNet2DConditionModel:
        unet_config = create_unet_diffusers_config(
            config, image_size=(768 if self._size_768 else 512)
        )

        unet = diffusers.UNet2DConditionModel(**unet_config)

        unet_weights = convert_ldm_unet_checkpoint(
            ckpt, unet_config, extract_ema=self._use_ema
        )

        unet.load_state_dict(unet_weights)

        return unet

    def _load_vae(self, ckpt, config):
        vae_config = create_vae_diffusers_config(
            config, image_size=(768 if self._size_768 else 512)
        )

        vae = diffusers.AutoencoderKL(**vae_config)

        vae_weights = convert_ldm_vae_checkpoint(ckpt, vae_config)

        vae.load_state_dict(vae_weights)

        return vae

    def _load_clip(self, ckpt, config):
        if (
            clip_type := config.model.params.cond_stage_config.target.split(".")[-1]
            == "FrozenOpenCLIPEmbedder"
        ):
            clip = convert_open_clip_checkpoint(ckpt)
        elif clip_type == "FrozenCLIPEmbedder":
            clip = convert_ldm_clip_checkpoint(ckpt)

        return clip
