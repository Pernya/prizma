from __future__ import annotations

import argparse
from pathlib import Path

from common import read_json, read_params


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the Prizma model card.")
    parser.add_argument("--params", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--drift", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    params = read_params(args.params)
    model = read_json(args.model)
    benchmark = read_json(args.benchmark)
    drift = read_json(args.drift)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(_render(params, model, benchmark, drift), encoding="utf-8")


def _render(
    params: dict[str, object],
    model: dict[str, object],
    benchmark: dict[str, object],
    drift: dict[str, object],
) -> str:
    return f"""# Prizma Stylizer Model Card

## Identity

- Model name: `{model["name"]}`
- Version: `{model["version"]}`
- Alias: `{model["champion_alias"]}`
- Framework: `{model["framework"]}`
- Artifact type: `{model["artifact_type"]}`

## Intended Use

This baseline model serves the Prizma MVP image stylization flow. It accepts an image and a
style name, returns a PNG image, and preserves the Triton-compatible inference contract used by
the production architecture.

## Supported Styles

{chr(10).join(f"- `{style}`" for style in model["styles"])}

## Evaluation

- Golden-set samples: `{benchmark["samples"]}`
- Success rate: `{benchmark["success_rate"]:.4f}`
- Latency report: `reports/mlops/benchmark.json`
- Gate passed: `{benchmark["passed"]}`
- P95 threshold: `{params["evaluation"]["max_p95_latency_ms"]} ms`

## Drift

- Drift status: `{drift["status"]}`
- Drift score: `{drift["score"]:.4f}`
- Warning threshold: `{params["drift"]["warning_threshold"]}`
- Critical threshold: `{params["drift"]["critical_threshold"]}`

## Limitations

- This is not a learned neural stylization model; it is a deterministic Pillow baseline.
- Visual quality is acceptable only for MVP demonstration and infrastructure validation.
- Production promotion requires a trained model, human review, golden-set evaluation, canary
  rollout, and rollback rehearsal.

## Promotion Criteria

1. Benchmark gate passes on the golden set.
2. Drift report is not critical.
3. Model metadata is registered in MLflow with a candidate alias.
4. Canary analysis passes against API error rate and latency.
5. SRE owner confirms rollback path.
"""


if __name__ == "__main__":
    main()
