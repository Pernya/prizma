from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "prizma-backend"
    environment: str = "dev"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    base_url: str = "http://localhost:8000"
    local_artifact_dir: Path = Path("data/artifacts")
    job_state_dir: Path = Path("data/state/jobs")
    max_upload_bytes: int = 10 * 1024 * 1024
    allowed_content_types: tuple[str, ...] = ("image/jpeg", "image/png", "image/webp")
    execution_mode: Literal["direct", "broker"] = "direct"
    storage_backend: Literal["local", "s3"] = "local"
    artifact_bucket: str = "prizma-artifacts"
    s3_endpoint_url: str | None = None
    s3_region_name: str = "us-east-1"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/%2f"
    rabbitmq_queue: str = "prizma.jobs"
    inference_backend: Literal["local", "triton"] = "local"
    triton_url: str = "localhost:8000"
    triton_model_name: str = "prizma_stylizer"
    triton_timeout_seconds: float = 30.0
    worker_metrics_port: int = 9100

    model_config = SettingsConfigDict(env_prefix="PRIZMA_", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.local_artifact_dir.mkdir(parents=True, exist_ok=True)
    settings.job_state_dir.mkdir(parents=True, exist_ok=True)
    return settings
