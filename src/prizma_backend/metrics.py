from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter

from prometheus_client import Counter, Gauge, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "prizma_http_requests_total",
    "Total number of HTTP requests.",
    labelnames=("method", "path", "status"),
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "prizma_http_request_duration_seconds",
    "HTTP request latency in seconds.",
    labelnames=("method", "path"),
    buckets=(0.01, 0.05, 0.1, 0.3, 0.5, 1, 2, 3, 5, 10),
)
JOBS_TOTAL = Counter(
    "prizma_jobs_total",
    "Total number of processing jobs.",
    labelnames=("style", "result"),
)
JOB_DURATION_SECONDS = Histogram(
    "prizma_job_duration_seconds",
    "Job execution time in seconds.",
    labelnames=("style",),
    buckets=(0.1, 0.3, 0.5, 1, 2, 3, 5, 10, 20),
)
ACTIVE_JOBS = Gauge(
    "prizma_active_jobs",
    "Number of currently running jobs.",
)


def record_request(method: str, path: str, status: int, duration_seconds: float) -> None:
    HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status=str(status)).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(duration_seconds)


@contextmanager
def track_job(style: str) -> Iterator[None]:
    ACTIVE_JOBS.inc()
    started_at = perf_counter()
    result = "success"

    try:
        yield
    except Exception:
        result = "error"
        raise
    finally:
        ACTIVE_JOBS.dec()
        JOBS_TOTAL.labels(style=style, result=result).inc()
        JOB_DURATION_SECONDS.labels(style=style).observe(perf_counter() - started_at)
