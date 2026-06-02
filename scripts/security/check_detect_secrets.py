from __future__ import annotations

import json
import subprocess  # nosec B404
import sys
from typing import Any

EXCLUDE_FILES = (
    r"(^|/)(\.git|\.venv|data|models|reports|\.pytest_cache|\.ruff_cache|"
    r"\.tools|node_modules|dist|build)/"
)


def main() -> None:
    command = [
        "detect-secrets",
        "scan",
        "--all-files",
        "--disable-plugin",
        "KeywordDetector",
        "--exclude-files",
        EXCLUDE_FILES,
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)  # nosec B603
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)

    payload: dict[str, Any] = json.loads(completed.stdout)
    results: dict[str, list[dict[str, Any]]] = payload.get("results", {})
    findings = [(filename, item) for filename, items in sorted(results.items()) for item in items]
    if findings:
        print("Potential secrets detected:")
        for filename, item in findings:
            line = item.get("line_number", "?")
            secret_type = item.get("type", "unknown")
            print(f"- {filename}:{line} {secret_type}")
        raise SystemExit(1)

    print("No secrets detected")


if __name__ == "__main__":
    main()
