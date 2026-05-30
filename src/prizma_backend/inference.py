from __future__ import annotations

import base64
from io import BytesIO

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from tritonclient.http import InferenceServerClient, InferInput, InferRequestedOutput

from prizma_backend.config import Settings

STYLES: dict[str, str] = {
    "noir": "Контрастный монохромный фильтр.",
    "vivid": "Насыщенная цветовая обработка с усилением контраста.",
    "sketch": "Псевдо-карандашный стиль с выделением границ.",
    "warm": "Тёплый стиль для portrait-like обработки.",
}


class InferenceEngine:
    def infer(self, payload: bytes, style: str) -> bytes:
        raise NotImplementedError


class LocalInferenceEngine(InferenceEngine):
    def infer(self, payload: bytes, style: str) -> bytes:
        image = Image.open(BytesIO(payload)).convert("RGB")
        rendered = apply_style(image, style)
        buffer = BytesIO()
        rendered.save(buffer, format="PNG")
        return buffer.getvalue()


class TritonInferenceEngine(InferenceEngine):
    def __init__(self, settings: Settings) -> None:
        self.client = InferenceServerClient(url=settings.triton_url, verbose=False)
        self.model_name = settings.triton_model_name

    def infer(self, payload: bytes, style: str) -> bytes:
        image_b64 = base64.b64encode(payload).decode("ascii")
        image_input = InferInput("IMAGE_B64", [1], "BYTES")
        style_input = InferInput("STYLE", [1], "BYTES")
        image_input.set_data_from_numpy(np.array([image_b64], dtype=object))
        style_input.set_data_from_numpy(np.array([style], dtype=object))

        result = self.client.infer(
            model_name=self.model_name,
            inputs=[image_input, style_input],
            outputs=[InferRequestedOutput("IMAGE_B64")],
        )
        rendered = result.as_numpy("IMAGE_B64")[0]
        encoded = rendered.decode("utf-8") if isinstance(rendered, bytes) else str(rendered)
        return base64.b64decode(encoded)


def apply_style(image: Image.Image, style: str) -> Image.Image:
    if style == "noir":
        return ImageOps.grayscale(image).convert("RGB")

    if style == "vivid":
        image = ImageEnhance.Color(image).enhance(1.8)
        return ImageEnhance.Contrast(image).enhance(1.2)

    if style == "sketch":
        gray = ImageOps.grayscale(image)
        edges = gray.filter(ImageFilter.FIND_EDGES)
        inverted = ImageOps.invert(edges)
        return ImageOps.colorize(inverted, black="#101010", white="#f7f2ea")

    if style == "warm":
        red, green, blue = image.split()
        red = red.point(lambda value: min(255, int(value * 1.08)))
        blue = blue.point(lambda value: max(0, int(value * 0.92)))
        merged = Image.merge("RGB", (red, green, blue))
        return ImageEnhance.Contrast(merged).enhance(1.05)

    raise ValueError(f"Unsupported style: {style}")


def build_inference_engine(settings: Settings) -> InferenceEngine:
    if settings.inference_backend == "triton":
        return TritonInferenceEngine(settings)
    return LocalInferenceEngine()
