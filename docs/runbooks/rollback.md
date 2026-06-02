# Rollback Runbook

## API/Image Rollback

1. Identify the last healthy image tag in GitLab registry.
2. Update Helm value `image.tag` to the healthy tag.
3. Sync Argo CD or run `helm upgrade --install`.
4. Verify `/healthz`, `/readyz`, `/api/v1/styles` and one smoke job.
5. Confirm API error rate and p95 latency return below SLO alert thresholds.

## Canary Abort

If Argo Rollouts analysis fails:

```bash
kubectl argo rollouts abort rollout/prizma-api -n prizma
kubectl argo rollouts promote rollout/prizma-api -n prizma --full
```

Then inspect:

```bash
kubectl describe rollout prizma-api -n prizma
kubectl logs -n prizma deploy/prizma-worker
```

## Model Rollback

1. Repoint MLflow alias `champion` to the last approved model version.
2. Re-render Triton model repository if needed.
3. Restart or roll out Triton deployment.
4. Run golden-set benchmark and one public smoke job.
