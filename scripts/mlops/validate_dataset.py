from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

from common import image_paths, read_params, write_json
from PIL import Image, UnidentifiedImageError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Prizma image dataset quality gates.")
    parser.add_argument("--params", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    params = read_params(args.params)
    paths = image_paths(args.input)
    expected_samples = int(params["dataset"]["samples"])
    failures: list[str] = []
    seen_hashes: set[str] = set()

    if len(paths) < expected_samples:
        failures.append(f"expected at least {expected_samples} images, found {len(paths)}")

    dimensions: list[dict[str, object]] = []
    for path in paths:
        try:
            payload = path.read_bytes()
            digest = sha256(payload).hexdigest()
            if digest in seen_hashes:
                failures.append(f"{path.name}: duplicate image payload")
            seen_hashes.add(digest)

            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
                if width < 32 or height < 32:
                    failures.append(f"{path.name}: image is too small: {width}x{height}")
                dimensions.append(
                    {
                        "file": path.name,
                        "width": width,
                        "height": height,
                        "mode": image.mode,
                    }
                )
        except (OSError, UnidentifiedImageError) as exc:
            failures.append(f"{path.name}: invalid image: {exc}")

    report = {
        "input": str(args.input),
        "samples": len(paths),
        "expected_min_samples": expected_samples,
        "dimensions": dimensions,
        "failures": failures,
        "passed": not failures,
    }
    write_json(args.output, report)
    if failures:
        raise SystemExit("Dataset validation gate failed.")


if __name__ == "__main__":
    main()
