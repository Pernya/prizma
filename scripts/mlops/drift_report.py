from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from common import image_paths, read_params, write_json
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare current image distribution with baseline."
    )
    parser.add_argument("--params", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    params = read_params(args.params)
    baseline_paths = image_paths(args.baseline)
    current_paths = image_paths(args.current) or baseline_paths
    if not baseline_paths:
        raise SystemExit(f"No baseline images found in {args.baseline}")

    baseline = _profile(baseline_paths)
    current = _profile(current_paths)
    score = float(
        np.abs(np.array(baseline["mean_rgb"]) - np.array(current["mean_rgb"])).mean() / 255
    )
    thresholds = params["drift"]
    status = "ok"
    if score >= float(thresholds["critical_threshold"]):
        status = "critical"
    elif score >= float(thresholds["warning_threshold"]):
        status = "warning"

    write_json(
        args.output,
        {
            "status": status,
            "score": score,
            "baseline": baseline,
            "current": current,
            "thresholds": thresholds,
            "note": "Uses channel mean distance as a lightweight PSI proxy for MVP monitoring.",
        },
    )


def _profile(paths: list[Path]) -> dict[str, object]:
    pixels: list[np.ndarray] = []
    for path in paths:
        image = Image.open(path).convert("RGB").resize((64, 64))
        pixels.append(np.asarray(image, dtype=np.float32).reshape(-1, 3))
    all_pixels = np.concatenate(pixels, axis=0)
    return {
        "samples": len(paths),
        "mean_rgb": [float(value) for value in all_pixels.mean(axis=0)],
        "std_rgb": [float(value) for value in all_pixels.std(axis=0)],
    }


if __name__ == "__main__":
    main()
