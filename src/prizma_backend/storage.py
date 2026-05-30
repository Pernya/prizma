from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import boto3
from botocore.client import Config as BotoConfig

from prizma_backend.config import Settings


@dataclass(slots=True)
class StoredObject:
    key: str
    payload: bytes
    content_type: str


class ArtifactStorage:
    def put_bytes(self, key: str, payload: bytes, content_type: str) -> str:
        raise NotImplementedError

    def get_bytes(self, key: str, default_content_type: str) -> StoredObject:
        raise NotImplementedError


class LocalArtifactStorage(ArtifactStorage):
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def put_bytes(self, key: str, payload: bytes, content_type: str) -> str:
        path = self.root_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return key

    def get_bytes(self, key: str, default_content_type: str) -> StoredObject:
        path = self.root_dir / key
        return StoredObject(key=key, payload=path.read_bytes(), content_type=default_content_type)


class S3ArtifactStorage(ArtifactStorage):
    def __init__(self, settings: Settings) -> None:
        self.bucket = settings.artifact_bucket
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region_name,
            config=BotoConfig(s3={"addressing_style": "path"}),
        )

    def put_bytes(self, key: str, payload: bytes, content_type: str) -> str:
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=payload,
            ContentType=content_type,
        )
        return key

    def get_bytes(self, key: str, default_content_type: str) -> StoredObject:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        content_type = response.get("ContentType") or default_content_type
        payload = response["Body"].read()
        return StoredObject(key=key, payload=payload, content_type=content_type)


def build_storage(settings: Settings) -> ArtifactStorage:
    if settings.storage_backend == "s3":
        return S3ArtifactStorage(settings)
    return LocalArtifactStorage(settings.local_artifact_dir)
