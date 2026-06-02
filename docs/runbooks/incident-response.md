# Incident Response Runbook

## Triage

1. Check API health: `/healthz` and `/readyz`.
2. Check Prometheus alerts for error rate, latency and stuck jobs.
3. Check RabbitMQ queue depth and worker logs.
4. Check MinIO/S3 availability.
5. Check Cloudflare Tunnel status if public API is exposed from a local machine.

## Mitigation

- If API is unhealthy, roll back image tag.
- If queue is growing, scale workers or pause new uploads.
- If storage is failing, stop accepting new jobs until writes are healthy.
- If model quality regressed, roll back model alias and abort canary.

## Communication

- Record start time, affected endpoint and customer impact.
- Keep a timeline of actions.
- Produce a postmortem with root cause, detection gap and prevention action.
