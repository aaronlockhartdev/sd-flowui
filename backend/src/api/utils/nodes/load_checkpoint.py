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

from .node import Node


class LoadCheckpoint(Node):
    def __init__(self):
        ckpts = [
            os.path.join(path, name)
            for path, _, name in os.walk(
                os.path.join(env["DATA_DIR"], "models", "checkpoints")
            )
        ]

        configs = [
            os.path.join(path, name)
            for path, _, name in os.walk(os.path.join(env["DATA_DIR"], "configs"))
        ]

        super().__init__(
            outputs={
                "clip": {"name": "CLIP", "type": transformers.CLIPTextModel},
                "unet": {"name": "UNet", "type": diffusers.UNet2DConditionModel},
                "vae": {"name": "VAE", "type": diffusers.AutoencoderKL},
            },
            params={
                "ckpt_path": {
                    "name": "Checkpoint",
                    "type": str,
                    "default": "",
                    "selection": ckpts,
                },
                "cfg_path": {
                    "name": "Config",
                    "type": str,
                    "default": "",
                    "selection": configs,
                },
                "upcast_att": {
                    "name": "Upcast Attention",
                    "type": bool,
                    "default": False,
                },
                "use_ema": {"name": "Use EMA", "type": bool, "default": True},
                "size_768": {"name": "768 Model", "type": bool, "default": True},
            },
        )

    def __call__(self) -> None:
        config_path = os.path.join(env["DATA_DIR"], "configs", self._cfg_path)
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        ckpt_path = os.path.oin(
            env["DATA_DIR"], "models", "checkpoints", self._ckpt_path
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
            ckpt, unet_config, path=self._ckpt_path, extract_ema=self._use_ema
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
