import json
from pathlib import Path

from scripts.contracts.export_openapi import build_schema


def test_openapi_contract_is_current() -> None:
    expected = json.loads(Path("docs/api/openapi.json").read_text(encoding="utf-8"))

    assert build_schema() == expected
