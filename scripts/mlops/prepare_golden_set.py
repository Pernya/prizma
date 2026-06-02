from __future__ import annotations

import argparse
import random
from pathlib import Path

from common import read_params
from PIL import Image, ImageDraw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a deterministic synthetic golden set.")
    parser.add_argument("--params", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    params = read_params(args.params)
    seed = int(params["dataset"]["seed"])
    size = int(params["dataset"]["image_size"])
    samples = int(params["dataset"]["samples"])
    random.seed(seed)

    args.output.mkdir(parents=True, exist_ok=True)
    for existing in args.output.glob("*.png"):
        existing.unlink()

    for index in range(samples):
        base = Image.new("RGB", (size, size), _color(index, seed))
        draw = ImageDraw.Draw(base)
        # Deterministic pseudo-random geometry is enough for a synthetic golden set.
        for _ in range(8):
            x0 = random.randint(0, size - 16)  # nosec B311
            y0 = random.randint(0, size - 16)  # nosec B311
            x1 = random.randint(x0 + 8, size)  # nosec B311
            y1 = random.randint(y0 + 8, size)  # nosec B311
            draw.rectangle((x0, y0, x1, y1), outline=_color(index + x0 + y0, seed), width=2)
        draw.text((8, 8), f"golden-{index}", fill=(245, 245, 235))
        base.save(args.output / f"golden-{index:02d}.png")


def _color(value: int, seed: int) -> tuple[int, int, int]:
    return (
        (value * 37 + seed * 3) % 256,
        (value * 53 + seed * 5) % 256,
        (value * 71 + seed * 7) % 256,
    )


if __name__ == "__main__":
    main()
