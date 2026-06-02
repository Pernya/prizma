from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from prizma_backend.config import Settings
from prizma_backend.main import create_app


def _sample_image_bytes() -> bytes:
    image = Image.new("RGB", (32, 32), color=(20, 40, 180))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_health_endpoint(tmp_path: Path) -> None:
    app = create_app(
        Settings(
            local_artifact_dir=tmp_path / "artifacts",
            job_state_dir=tmp_path / "jobs",
            base_url="http://testserver",
        )
    )
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_job_lifecycle(tmp_path: Path) -> None:
    app = create_app(
        Settings(
            local_artifact_dir=tmp_path / "artifacts",
            job_state_dir=tmp_path / "jobs",
            base_url="http://testserver",
        )
    )
    client = TestClient(app)

    response = client.post(
        "/api/v1/jobs",
        data={"style": "noir"},
        files={"file": ("photo.png", _sample_image_bytes(), "image/png")},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "queued"

    details = client.get(payload["status_url"].replace("http://testserver", ""))
    assert details.status_code == 200
    assert details.json()["status"] == "succeeded"
    assert (
        details.json()["result_url"] == f"http://testserver/api/v1/jobs/{payload['job_id']}/result"
    )

    result = client.get(f"/api/v1/jobs/{payload['job_id']}/result")
    assert result.status_code == 200
    assert result.headers["content-type"] == "image/png"
    assert result.content


def test_job_urls_respect_forwarded_headers(tmp_path: Path) -> None:
    app = create_app(
        Settings(
            local_artifact_dir=tmp_path / "artifacts",
            job_state_dir=tmp_path / "jobs",
            base_url="http://localhost:8000",
        )
    )
    client = TestClient(app)

    response = client.post(
        "/api/v1/jobs",
        headers={
            "X-Forwarded-Proto": "https",
            "X-Forwarded-Host": "api.pernyaev.ru",
        },
        data={"style": "vivid"},
        files={"file": ("photo.png", _sample_image_bytes(), "image/png")},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status_url"].startswith("https://api.pernyaev.ru/api/v1/jobs/")

    details = client.get(
        payload["status_url"].replace("https://api.pernyaev.ru", ""),
        headers={
            "X-Forwarded-Proto": "https",
            "X-Forwarded-Host": "api.pernyaev.ru",
        },
    )

    assert details.status_code == 200
    assert details.json()["result_url"] == (
        f"https://api.pernyaev.ru/api/v1/jobs/{payload['job_id']}/result"
    )


def test_metrics_endpoint(tmp_path: Path) -> None:
    app = create_app(
        Settings(
            local_artifact_dir=tmp_path / "artifacts",
            job_state_dir=tmp_path / "jobs",
            base_url="http://testserver",
        )
    )
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "prizma_http_requests_total" in response.text
