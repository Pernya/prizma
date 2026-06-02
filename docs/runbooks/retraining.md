# Retraining Decision Runbook

## Triggers

- Drift report status is `warning` or `critical`.
- Golden-set score drops below champion baseline.
- New curated dataset is available.
- User feedback indicates repeated visual quality issues.

## Candidate Flow

1. Create DVC snapshot for dataset changes.
2. Run training and log MLflow run.
3. Generate benchmark report and model card.
4. Register candidate model version.
5. Deploy to staging and run integration smoke tests.
6. Run production canary with Argo Rollouts analysis.
7. Promote candidate to `champion` only after evaluation and SRE approval.

## Rejection Criteria

- P95 inference latency exceeds configured threshold.
- Golden-set quality regresses versus champion.
- Drift report is critical.
- Canary error rate or latency violates rollout thresholds.
