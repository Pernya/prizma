# Prizma Threat Model

## Assets

- User-uploaded source images.
- Rendered result images.
- RabbitMQ credentials.
- S3/MinIO credentials.
- API key when enabled.
- Model artifacts and model metadata.

## Main Risks

- Malicious file upload disguised as an image.
- Oversized upload causing memory pressure.
- Public API abuse when exposed through a tunnel or ingress.
- Secret leakage in repository or CI logs.
- Stale images retained longer than intended.
- Model artifact rollback failure.

## Controls

- Content type allow-list.
- Image payload verification before persistence.
- Upload size limit.
- Optional `X-API-Key` gate for job creation.
- Secret detection and dependency scanning jobs.
- Kubernetes existing Secret or ExternalSecret integration for production values.
- Retention cleanup job for expired images and job metadata.
- Canary analysis before production rollout.

## Open Items

- Add user authentication when the product moves beyond public demo.
- Add malware scanning for uploads if the service stores user content at scale.
