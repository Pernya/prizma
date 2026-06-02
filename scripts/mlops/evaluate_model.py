from __future__ import annotations

import argparse
import statistics
from pathlib import Path
from time import perf_counter

from common import image_paths, read_json, read_params, write_json
from PIL import Image

from prizma_backend.inference import apply_style


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate style inference on a golden set.")
    parser.add_argument("--params", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    params = read_params(args.params)
    model = read_json(args.model)
    styles = list(model["styles"])
    paths = image_paths(args.input)
    if not paths:
        raise SystemExit(f"No images found in {args.input}")

    latencies_ms: list[float] = []
    failures: list[str] = []
    for image_path in paths:
        image = Image.open(image_path).convert("RGB")
        for style in styles:
            started = perf_counter()
            try:
                rendered = apply_style(image, style)
                rendered.load()
            except Exception as exc:
                failures.append(f"{image_path.name}:{style}:{exc}")
            latencies_ms.append((perf_counter() - started) * 1000)

    success_count = len(paths) * len(styles) - len(failures)
    success_rate = success_count / (len(paths) * len(styles))
    p95 = _quantile(latencies_ms, 0.95)
    thresholds = params["evaluation"]
    passed = success_rate >= float(thresholds["min_success_rate"]) and p95 <= float(
        thresholds["max_p95_latency_ms"]
    )
    write_json(
        args.output,
        {
            "model": model["name"],
            "version": model["version"],
            "samples": len(paths),
            "styles": styles,
            "success_rate": success_rate,
            "latency_ms": {
                "min": min(latencies_ms),
                "mean": statistics.fmean(latencies_ms),
                "p95": p95,
                "max": max(latencies_ms),
            },
            "thresholds": thresholds,
            "failures": failures,
            "passed": passed,
        },
    )
    if not passed:
        raise SystemExit("Model evaluation gate failed.")


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[index]


if __name__ == "__main__":
    main()
