from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from prizma_backend.config import Settings
from prizma_backend.inference import STYLES, InferenceEngine, build_inference_engine
from prizma_backend.messaging import RabbitMQPublisher
from prizma_backend.metrics import track_job
from prizma_backend.models import JobCreated, JobDetails, JobRecord, JobStatus, StyleInfo
from prizma_backend.repository import FileJobRepository
from prizma_backend.storage import ArtifactStorage, StoredObject, build_storage


class JobService:
    def __init__(
        self,
        settings: Settings,
        repository: FileJobRepository,
        storage: ArtifactStorage,
        inference_engine: InferenceEngine,
        publisher: RabbitMQPublisher | None = None,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.storage = storage
        self.inference_engine = inference_engine
        self.publisher = publisher

    def list_styles(self) -> list[StyleInfo]:
        return [
            StyleInfo(name=name, description=description) for name, description in STYLES.items()
        ]

    def create_job(self, file: UploadFile, style: str) -> JobRecord:
        self._validate_style(style)
        self._validate_content_type(file.content_type)

        payload = file.file.read()
        if len(payload) > self.settings.max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds {self.settings.max_upload_bytes} bytes.",
            )

        job_id = uuid4().hex
        safe_stem = self._safe_stem(file.filename or "upload")
        suffix = Path(file.filename or "upload").suffix or ".bin"
        source_key = f"uploads/{job_id}/{safe_stem}{suffix}"
        record = JobRecord(
            job_id=job_id,
            status=JobStatus.queued,
            style=style,
            source_filename=file.filename or "upload",
            source_key=source_key,
        )
        self.storage.put_bytes(
            key=source_key,
            payload=payload,
            content_type=file.content_type or "application/octet-stream",
        )
        self.repository.create(record)
        return record

    def dispatch_job(self, job_id: str) -> None:
        if self.settings.execution_mode != "broker":
            raise RuntimeError("dispatch_job is only available in broker mode.")
        if self.publisher is None:
            raise RuntimeError("RabbitMQ publisher is not configured.")
        self.publisher.publish(job_id)

    def process_job(self, job_id: str) -> None:
        job = self.repository.require(job_id)
        job.status = JobStatus.running
        job.error = None
        self.repository.save(job)

        try:
            with track_job(job.style):
                source = self.storage.get_bytes(
                    key=job.source_key,
                    default_content_type="application/octet-stream",
                )
                rendered = self.inference_engine.infer(source.payload, job.style)

            result_filename = f"{self._safe_stem(job.source_filename)}-{job.style}.png"
            result_key = f"results/{job.job_id}/{result_filename}"
            self.storage.put_bytes(key=result_key, payload=rendered, content_type="image/png")
            job.status = JobStatus.succeeded
            job.result_key = result_key
            job.finished_at = datetime.now(timezone.utc)
            self.repository.save(job)
        except Exception as exc:
            job.status = JobStatus.failed
            job.error = str(exc)
            job.finished_at = datetime.now(timezone.utc)
            self.repository.save(job)

    def get_job(self, job_id: str) -> JobDetails:
        job = self.repository.get(job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

        result_url = None
        if job.result_key:
            result_url = f"{self.settings.base_url}/api/v1/jobs/{job.job_id}/result"

        return JobDetails(
            job_id=job.job_id,
            status=job.status,
            style=job.style,
            source_filename=job.source_filename,
            result_url=result_url,
            error=job.error,
            created_at=job.created_at,
            finished_at=job.finished_at,
        )

    def get_result(self, job_id: str) -> StoredObject:
        job = self.repository.get(job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
        if job.status != JobStatus.succeeded or not job.result_key:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Job result is not available yet.",
            )
        return self.storage.get_bytes(job.result_key, default_content_type="image/png")

    @staticmethod
    def build_created_response(base_url: str, record: JobRecord) -> JobCreated:
        return JobCreated(
            job_id=record.job_id,
            status=record.status,
            status_url=f"{base_url}/api/v1/jobs/{record.job_id}",
        )

    def _validate_style(self, style: str) -> None:
        if style not in STYLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported style. Choose one of: {', '.join(STYLES)}.",
            )

    def _validate_content_type(self, content_type: str | None) -> None:
        if content_type not in self.settings.allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported content type: {content_type}.",
            )

    @staticmethod
    def _safe_stem(filename: str) -> str:
        safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", Path(filename).stem).strip("-")
        return safe_stem or "image"


def build_job_service(settings: Settings) -> JobService:
    publisher = RabbitMQPublisher(settings) if settings.execution_mode == "broker" else None
    return JobService(
        settings=settings,
        repository=FileJobRepository(settings.job_state_dir),
        storage=build_storage(settings),
        inference_engine=build_inference_engine(settings),
        publisher=publisher,
    )
