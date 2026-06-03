from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import gettempdir

from prizma_backend.config import Settings
from prizma_backend.main import create_app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export FastAPI OpenAPI schema.")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def build_schema() -> dict[str, object]:
    tmp_root = Path(gettempdir()) / "prizma-openapi"
    app = create_app(
        Settings(
            local_artifact_dir=tmp_root / "artifacts",
            job_state_dir=tmp_root / "jobs",
            base_url="http://localhost:8000",
        )
    )
    return app.openapi()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_schema(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
