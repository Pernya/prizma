from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel


class JobStatus(StrEnum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class StyleInfo(BaseModel):
    name: str
    description: str


class JobCreated(BaseModel):
    job_id: str
    status: JobStatus
    status_url: str


class JobDetails(BaseModel):
    job_id: str
    status: JobStatus
    style: str
    source_filename: str
    result_url: str | None
    error: str | None
    created_at: datetime
    finished_at: datetime | None


@dataclass(slots=True)
class JobRecord:
    job_id: str
    status: JobStatus
    style: str
    source_filename: str
    source_key: str
    result_key: str | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
