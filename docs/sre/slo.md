# Prizma SLO and Error Budget

This document turns the case-report SRE targets into explicit, checkable operating goals.

## Scope

The SLOs cover the public Prizma image-stylization flow:

- User opens the public frontend.
- User uploads an image and creates a processing job.
- Backend accepts the job, dispatches it to worker/inference, stores the artifact, and returns the result URL.
- User downloads or shares the processed result.

## Service Level Objectives

| Area | SLI | SLO | Primary signal |
| --- | --- | --- | --- |
| API availability | Successful API requests / all API requests | >= 99.9% monthly | `prizma_http_requests_total` |
| API error rate | 5xx API requests / all API requests | < 1% over 10 minutes | `prizma_http_requests_total{status=~"5.."}` |
| Job creation latency | p95 latency for `POST /api/v1/jobs` | <= 300 ms over 10 minutes | `prizma_http_request_duration_seconds_bucket{path="/api/v1/jobs"}` |
| Processing latency | p95 end-to-end job duration | <= 2.5 s over 10 minutes | `prizma_job_duration_seconds_bucket` |
| Processing reliability | Failed jobs / all completed jobs | < 1% over 10 minutes | `prizma_jobs_total{result="error"}` |
| Queue pressure | Active jobs waiting or processing | <= 10 active jobs for 10 minutes | `prizma_active_jobs` |
| Rollback time | Time from bad deploy detection to previous stable version | <= 15 minutes | Rollback runbook timestamp |
| Model quality gate | Benchmark success rate and p95 latency | Must pass before release | `reports/mlops/benchmark.json` |
| Data quality gate | Dataset validity, duplicates, minimum sample count | Must pass before training/evaluation | `reports/mlops/data-validation.json` |

## Error Budget Policy

- If API availability drops below 99.9% for the current month, feature deploys stop until the rollback or remediation is completed.
- If any Prometheus SLO alert fires for more than 10 minutes, the on-call owner follows `docs/runbooks/incident-response.md`.
- If rollback is required, use `docs/runbooks/rollback.md` and record detection, decision, and recovery timestamps.
- If model or data gates fail, block promotion and follow `docs/runbooks/retraining.md`.

## Prometheus Alerts

The alert implementation is stored in `observability/prometheus/prizma-rules.yml`.

Current alert coverage:

- `PrizmaHighErrorRate` maps to API error-rate SLO.
- `PrizmaHighP95Latency` maps to job creation latency SLO.
- `PrizmaHighJobP95Duration` maps to processing latency SLO.
- `PrizmaHighJobFailureRate` maps to processing reliability SLO.
- `PrizmaJobsStuck` maps to queue pressure SLO.

## Release Gate

Before promoting a release:

- `make lint`
- `make test`
- `make security`
- `make contract`
- `make mlops`
- `make kube-validate`

Promotion is allowed only when all gates pass and the current production alert state is green.
