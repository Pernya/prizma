# Prizma Stylizer Model Card

## Identity

- Model name: `prizma_stylizer`
- Version: `baseline-pillow-v1`
- Alias: `champion`
- Framework: `Pillow baseline with Triton-compatible contract`
- Artifact type: `metadata-only-baseline`

## Intended Use

This baseline model serves the Prizma MVP image stylization flow. It accepts an image and a
style name, returns a PNG image, and preserves the Triton-compatible inference contract used by
the production architecture.

## Supported Styles

- `noir`
- `vivid`
- `sketch`
- `warm`

## Evaluation

- Golden-set samples: `8`
- Success rate: `1.0000`
- Mean latency: `0.22 ms`
- P95 latency: `0.33 ms`
- Gate passed: `True`
- P95 threshold: `2500 ms`

## Drift

- Drift status: `ok`
- Drift score: `0.0000`
- Warning threshold: `0.12`
- Critical threshold: `0.25`

## Limitations

- This is not a learned neural stylization model; it is a deterministic Pillow baseline.
- Visual quality is acceptable only for MVP demonstration and infrastructure validation.
- Production promotion requires a trained model, human review, golden-set evaluation, canary
  rollout, and rollback rehearsal.

## Promotion Criteria

1. Benchmark gate passes on the golden set.
2. Drift report is not critical.
3. Model metadata is registered in MLflow with a candidate alias.
4. Canary analysis passes against API error rate and latency.
5. SRE owner confirms rollback path.
