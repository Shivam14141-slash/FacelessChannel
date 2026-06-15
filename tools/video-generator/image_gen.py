"""
Image rendering via FLUX.1 [schnell] on fal.ai (replaces the Pillow-based
shapes.py renderer — see decisions-log.md for why).

STYLE_PREFIX is the "v2" style block validated against the Zenn reference
frames (Testing/reference_frames/) — locked as the baseline. Do not bloat
this with extra constraints without re-testing against the reference frames;
v3 (heavier constraints) measurably made results worse on this model.
"""

from __future__ import annotations

import os
import time

import requests

FAL_MODEL = "fal-ai/flux/schnell"

STYLE_PREFIX = (
    "Flat 2D vector illustration in extremely simple amateur MS Paint hand-drawn style. "
    "Thick uneven black outlines, wobbly hand-drawn lines. "
    "Completely flat solid colors only — absolutely NO shading, NO gradients, NO highlights, "
    "NO 3D, NO cinematic lighting, NO glossy or modern design, NO Disney style, NO anime style, "
    "NO polished illustration, NO professional vector art, NO realistic textures. "
    "Stick-figure humans with round circle heads, simple oval or dot eyes, line bodies, basic expressions. "
    "Mostly empty simple backgrounds. 16:9 widescreen composition, wide and clear, nothing cropped."
)


def generate_image(scene_description: str, out_path: str,
                    image_size: str = "landscape_16_9", max_retries: int = 3) -> str:
    """
    Generate one image for scene_description (a plain-English description of
    the scene content) via FLUX Schnell on fal.ai, and save it to out_path.
    Returns out_path.
    """
    fal_key = os.environ["FAL_KEY"]
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    prompt = f"{STYLE_PREFIX} Scene: {scene_description}"
    body = {"prompt": prompt, "image_size": image_size, "num_images": 1}

    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(f"https://fal.run/{FAL_MODEL}", headers=headers, json=body, timeout=120)
            resp.raise_for_status()
            img_url = resp.json()["images"][0]["url"]
            img_data = requests.get(img_url, timeout=60).content
            with open(out_path, "wb") as f:
                f.write(img_data)
            return out_path
        except Exception as e:  # noqa: BLE001 - retry on any transient error
            last_err = e
            if attempt < max_retries:
                time.sleep(2 * attempt)
    raise RuntimeError(f"Image generation failed for {out_path!r} after {max_retries} attempts: {last_err}")
