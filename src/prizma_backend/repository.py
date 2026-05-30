from __future__ import annotations

import json
import threading
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from prizma_backend.models import JobRecord, JobStatus


class FileJobRepository:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def create(self, job: JobRecord) -> None:
        self.save(job)

    def save(self, job: JobRecord) -> None:
        payload = self._serialize(job)
        path = self._job_path(job.job_id)
        tmp_path = path.with_suffix(".tmp")

        with self._lock:
            tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp_path.replace(path)

    def get(self, job_id: str) -> JobRecord | None:
        path = self._job_path(job_id)
        if not path.exists():
            return None
        return self._deserialize(json.loads(path.read_text(encoding="utf-8")))

    def require(self, job_id: str) -> JobRecord:
        job = self.get(job_id)
        if job is None:
            raise FileNotFoundError(f"Job {job_id} not found.")
        return job

    @staticmethod
    def _serialize(job: JobRecord) -> dict[str, object]:
        payload = asdict(job)
        payload["status"] = job.status.value
        payload["created_at"] = job.created_at.isoformat()
        payload["finished_at"] = job.finished_at.isoformat() if job.finished_at else None
        return payload

    @staticmethod
    def _deserialize(payload: dict[str, object]) -> JobRecord:
        return JobRecord(
            job_id=str(payload["job_id"]),
            status=JobStatus(str(payload["status"])),
            style=str(payload["style"]),
            source_filename=str(payload["source_filename"]),
            source_key=str(payload["source_key"]),
            result_key=str(payload["result_key"]) if payload.get("result_key") else None,
            error=str(payload["error"]) if payload.get("error") else None,
            created_at=datetime.fromisoformat(str(payload["created_at"])),
            finished_at=(
                datetime.fromisoformat(str(payload["finished_at"]))
                if payload.get("finished_at")
                else None
            ),
        )

    def _job_path(self, job_id: str) -> Path:
        return self.root_dir / f"{job_id}.json"
