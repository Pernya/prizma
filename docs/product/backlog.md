# Prizma MVP Backlog

## Epic: Image Stylization Flow

### Story: Upload image and create job

As a user, I can upload a PNG/JPEG/WebP image, choose a style and create a processing job.

Acceptance criteria:

- Reject unsupported content types.
- Reject invalid image payloads.
- Reject files above `PRIZMA_MAX_UPLOAD_BYTES`.
- Return a job id and public status URL.
- Queue the job when broker mode is enabled.

### Story: Poll job status

As a user, I can see whether processing is queued, running, succeeded or failed.

Acceptance criteria:

- Unknown job ids return `404`.
- Failed jobs expose a user-readable error.
- Succeeded jobs expose a public result URL.

### Story: Save or share result

As a user, I can download or share the processed PNG result.

Acceptance criteria:

- Result endpoint returns `409` until the job succeeds.
- Result endpoint returns `image/png`.
- Public frontend can load the result through the configured API/proxy route.
- Public frontend exposes download and share/copy controls after successful processing.

## Epic: MLOps Governance

### Story: Evaluate candidate model

Acceptance criteria:

- Candidate metadata is generated.
- Golden-set benchmark passes configured thresholds.
- Model card is updated from benchmark and drift report.
- Promotion requires human approval and canary analysis.

### Story: Monitor drift

Acceptance criteria:

- Current sample profile is compared against golden-set profile.
- Drift report produces `ok`, `warning` or `critical`.
- Critical drift blocks automatic promotion.
