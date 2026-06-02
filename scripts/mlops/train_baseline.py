from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from common import read_params, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register baseline model metadata.")
    parser.add_argument("--params", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    params = read_params(args.params)
    model = params["model"]
    payload = {
        "name": model["name"],
        "version": model["version"],
        "champion_alias": model["champion_alias"],
        "styles": model["styles"],
        "framework": "Pillow baseline with Triton-compatible contract",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "artifact_type": "metadata-only-baseline",
        "serving_contract": {
            "inputs": ["IMAGE_B64", "STYLE"],
            "outputs": ["IMAGE_B64"],
        },
    }
    write_json(args.output, payload)
    _log_mlflow_if_available(payload)


def _log_mlflow_if_available(payload: dict[str, object]) -> None:
    try:
        import mlflow  # type: ignore
    except Exception:
        return

    mlflow.set_experiment("prizma-stylizer")
    with mlflow.start_run(run_name=str(payload["version"])):
        mlflow.log_params(
            {
                "model_name": payload["name"],
                "model_version": payload["version"],
                "framework": payload["framework"],
            }
        )
        mlflow.set_tag("alias", payload["champion_alias"])


if __name__ == "__main__":
    main()
