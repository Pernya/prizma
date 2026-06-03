# Prizma Requirements Traceability

Source: `/Users/sanalpernyaev/Downloads/Prizma,команда 1.docx`.

This matrix tracks how the repository covers the target process and architecture described in the
case report.

| Requirement area | Document anchor | Repository coverage | Status |
| --- | --- | --- | --- |
| Mobile B2C user flow: upload, choose style, process, save/share | Sections 2, 5; Table 3 | Responsive installable web/PWA-like frontend in `web/`; result download/share controls; native mobile app is not implemented | Partial |
| Backend API / gateway | Section 4; Table 2 | FastAPI backend, validation, job lifecycle, metrics, static OpenAPI contract in `docs/api/openapi.json` | Covered |
| API contract quality gate | Tables 4, 9 | `make contract` exports OpenAPI; `tests/test_contract.py` blocks drift between app and committed schema | Covered |
| Queue for heavy processing | Section 4; Table 2 | RabbitMQ publisher/consumer, worker service, compose and Helm manifests | Covered |
| S3-compatible artifact storage | Section 4; Table 2 | MinIO/S3 storage backend, retention cleanup job, compose and Helm manifests | Covered |
| Triton-compatible inference | Section 4; Table 8 | Triton model repository scaffold and HTTP client integration; production GPU model is still a placeholder | Partial |
| DVC / dataset reproducibility | Sections 6, 8; Tables 4, 7, 8 | `dvc.yaml`, deterministic golden-set generation, generated datasets ignored for DVC remote tracking | Covered |
| Data validation gate | Tables 7, 9 | `scripts/mlops/validate_dataset.py` and `reports/mlops/data-validation.json` in MLOps pipeline | Covered |
| MLflow / model registry | Sections 6, 8; Table 8 | Optional MLflow logging in baseline training script and `.[mlops]` extra; no remote MLflow server configured | Partial |
| Model card and benchmark | Sections 6, 10; Tables 4, 9 | Generated `docs/mlops/model-card.md`, benchmark and drift reports | Covered |
| GitLab CI/CD | Section 8; Table 8 | `.gitlab-ci.yml` retained, but GitLab.com runners are blocked by account verification | Partial |
| GitHub CI/CD alternative | Section 8 adaptation | GitHub Actions CI, GHCR image publishing, manual Kubernetes deploy, VPS frontend deploy | Covered |
| GitOps / Argo CD | Sections 8, 10 | Argo CD Application manifests and Helm values; live GitOps sync is not connected to a real cluster | Partial |
| Progressive delivery | Tables 8, 9 | Argo Rollouts templates and Prometheus analysis gates | Covered as manifests |
| Kubernetes / Helm | Sections 4, 8 | Helm chart for API, worker, MinIO, RabbitMQ, Triton, ServiceMonitor, ExternalSecret, CronJob | Covered |
| Current public VPS deployment | Current implementation | GitHub Actions SSH deploy to VPS Docker Compose frontend | Covered |
| Prometheus/Grafana observability | Sections 10; Table 10 | Compose observability and Kubernetes observability manifests/rules | Covered |
| SLO/SLI | Section 10; Table 10 | Explicit SLO/error-budget document in `docs/sre/slo.md`, Prometheus alerts, dashboard and runbooks | Covered |
| Security gates | Section 9; Table 9 | secret detection, Bandit, pip-audit, image build, upload validation, ExternalSecret support | Covered |
| Rollback and incident response | Sections 10, 11 | rollback, incident response and retraining runbooks | Covered |
| Native mobile release/signing | Tables 5, 12 | Not implemented; outside current web/VPS MVP | Not covered |

## Current Coverage Summary

- Strong coverage: backend, queue/storage, MLOps baseline, CI quality gates, Helm/Kubernetes
  manifests, observability, SLOs, security, rollback, VPS CD.
- Partial coverage: native mobile client, production GPU model, live GitOps cluster, remote MLflow
  registry, dedicated CDN for result files.
- Practical next step for higher coverage: add real MLflow tracking URI, connect a managed
  Kubernetes cluster or keep VPS CD as the accepted deployment target, and decide whether native
  mobile is required or the responsive web client is sufficient for this case.
