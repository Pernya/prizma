from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
from tempfile import gettempdir
from time import sleep

import httpx
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Prizma public API smoke test.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--style", default="vivid")
    parser.add_argument("--timeout-seconds", type=float, default=60)
    parser.add_argument("--api-key", default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(gettempdir()) / "prizma-smoke-result.png",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    headers = {"X-API-Key": args.api_key} if args.api_key else {}
    base_url = args.base_url.rstrip("/")

    with httpx.Client(timeout=15.0, follow_redirects=True, headers=headers) as client:
        styles = client.get(f"{base_url}/api/v1/styles")
        styles.raise_for_status()
        style_names = {item["name"] for item in styles.json()}
        if args.style not in style_names:
            raise SystemExit(f"Style {args.style} is not available: {sorted(style_names)}")

        created = client.post(
            f"{base_url}/api/v1/jobs",
            data={"style": args.style},
            files={"file": ("smoke.png", _sample_png(), "image/png")},
        )
        created.raise_for_status()
        job = created.json()
        status_url = _normalize_url(base_url, job["status_url"])

        for _ in range(round(args.timeout_seconds)):
            details = client.get(status_url)
            details.raise_for_status()
            payload = details.json()
            if payload["status"] == "succeeded":
                result = client.get(_normalize_url(base_url, payload["result_url"]))
                result.raise_for_status()
                args.output.write_bytes(result.content)
                print(f"job_id={payload['job_id']} result={args.output}")
                return
            if payload["status"] == "failed":
                raise SystemExit(payload.get("error") or "Job failed")
            sleep(1)

    raise SystemExit("Smoke job timed out")


def _sample_png() -> bytes:
    image = Image.new("RGB", (64, 64), (64, 128, 220))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _normalize_url(base_url: str, value: str) -> str:
    parsed = httpx.URL(value)
    if parsed.host in {"localhost", "127.0.0.1"}:
        return f"{base_url}{parsed.path}"
    return value


if __name__ == "__main__":
    main()
