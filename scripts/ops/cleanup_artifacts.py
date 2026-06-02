from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from prizma_backend.config import Settings
from prizma_backend.storage import S3ArtifactStorage


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete expired Prizma job and artifact files.")
    parser.add_argument("--retention-days", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings()
    retention_days = args.retention_days or settings.artifact_retention_days
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    deleted = 0
    deleted += _delete_old_files(settings.job_state_dir, cutoff, args.dry_run)
    if settings.storage_backend == "s3":
        deleted += _delete_old_s3_objects(settings, cutoff, args.dry_run)
    else:
        deleted += _delete_old_files(settings.local_artifact_dir, cutoff, args.dry_run)
    print(f"expired_artifacts_deleted={deleted} dry_run={args.dry_run}")


def _delete_old_files(root: Path, cutoff: datetime, dry_run: bool) -> int:
    if not root.exists():
        return 0
    deleted = 0
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        if modified_at >= cutoff:
            continue
        deleted += 1
        if not dry_run:
            path.unlink()
    return deleted


def _delete_old_s3_objects(settings: Settings, cutoff: datetime, dry_run: bool) -> int:
    storage = S3ArtifactStorage(settings)
    deleted = 0
    paginator = storage.client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=storage.bucket):
        for item in page.get("Contents", []):
            last_modified = item["LastModified"]
            if last_modified >= cutoff:
                continue
            deleted += 1
            if not dry_run:
                storage.client.delete_object(Bucket=storage.bucket, Key=item["Key"])
    return deleted


if __name__ == "__main__":
    main()
