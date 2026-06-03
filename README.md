# Prizma Platform Skeleton

Production-oriented baseline для кейса Prizma из документа:

- FastAPI API
- асинхронный worker
- MinIO как S3-compatible artifact storage
- RabbitMQ как job broker
- Triton-compatible inference контур
- Grafana + Prometheus
- Kubernetes/Helm/Argo CD и GitLab CI/CD
- DVC-style MLOps pipeline, model card, drift/evaluation gates
- security gates and rollout/rollback runbooks

Текущий production hostname подготовлен под `prizma.pernyaev.ru`.

## Что реализовано

Сервис поддерживает:

- `GET /healthz` и `GET /readyz`
- `GET /api/v1/styles`
- `POST /api/v1/jobs` для загрузки изображения и запуска обработки
- `GET /api/v1/jobs/{job_id}` для статуса
- `GET /api/v1/jobs/{job_id}/result` для получения результата через API
- `GET /metrics` для Prometheus

Доступны два режима inference:

- `local`: стилизация через `Pillow`
- `triton`: вызов Triton Inference Server через официальный HTTP client

В репозитории есть Triton model-repository scaffold с минимальным Python backend-моделем, чтобы контракт и инфраструктура были готовы до подключения настоящей модели.

## Быстрый старт

Локальный запуск:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn prizma_backend.main:app --app-dir src --reload
```

Локальный platform-стенд:

```bash
docker compose -p prizma up -d --build
```

Публичный stand для обычного сервера за `95.163.244.138`:

```bash
docker compose -f docker-compose.server.yml -p prizma up -d --build
```

Если фронт должен жить на публичном сервере, а backend оставаться на Mac, используйте:

```bash
docker compose -f docker-compose.frontend-server.yml -p prizma-frontend up -d
```

API в этом режиме публикуется с Mac через Cloudflare Tunnel как `api.pernyaev.ru`.

Полезные URL:

- API: [http://localhost:8000/docs](http://localhost:8000/docs)
- MinIO API: [http://localhost:9000](http://localhost:9000)
- MinIO Console: [http://localhost:9001](http://localhost:9001)
- RabbitMQ UI: [http://localhost:15672](http://localhost:15672)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3000](http://localhost:3000)

Grafana по умолчанию использует `admin/admin`.
RabbitMQ по умолчанию использует `prizma/prizma`.
MinIO по умолчанию использует `minioadmin/minioadmin123`.

Если нужен Triton-контур локально:

```bash
PRIZMA_INFERENCE_BACKEND=triton docker compose -p prizma --profile triton up -d --build
```

## Структура

- [src/prizma_backend/main.py](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/src/prizma_backend/main.py)
- [tests/test_api.py](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/tests/test_api.py)
- [docker-compose.yml](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/docker-compose.yml)
- [charts/prizma](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/charts/prizma)
- [triton-model-repository](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/triton-model-repository)
- [deploy/k8s/observability](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/deploy/k8s/observability)
- [deploy/eks](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/deploy/eks)
- [deploy/regcloud](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/deploy/regcloud)
- [.gitlab-ci.yml](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/.gitlab-ci.yml)
- [.github/workflows/ci.yml](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/.github/workflows/ci.yml)
- [.github/workflows/deploy.yml](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/.github/workflows/deploy.yml)
- [.github/workflows/deploy-vps.yml](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/.github/workflows/deploy-vps.yml)
- [docs/git/remote-setup.md](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/docs/git/remote-setup.md)

## CI/CD и GitOps

Pipeline разбит на несколько контуров:

- software: lint, tests, dependency scan, image build
- mlops: golden set, baseline metadata, evaluation, drift report, model card
- security: SAST, secret detection, container scan, compose smoke test
- infra: Helm lint, manifest render, Kubernetes manifest validation for dev/prod/EKS/Reg.Cloud/rollout values

GitHub Actions запускает базовый CI без GitLab shared runners:

- Python lint/test/security gates
- MLOps gates
- Helm/kubeconform validation
- Docker image build and push to GHCR on `main`

GitHub CD запускается вручную через `Actions -> Deploy -> Run workflow`. Для этого нужно
добавить environment secret `KUBECONFIG_B64` в GitHub Environment `dev`, `regcloud` или `prod`.

Для текущего VPS-режима есть отдельный CD: `Actions -> Deploy VPS Frontend`.
Он доставляет `web/`, nginx-конфиг и `docker-compose.frontend-server.yml` на VPS по SSH и
перезапускает compose stack.

GitLab CI/CD остается подготовленным для GitLab runners и deploy jobs. CD можно вести двумя путями:

- `deploy-dev` и `deploy-prod` jobs через `helm upgrade --install`
- Argo CD через манифесты из `deploy/argocd/`

Для `EKS` добавлены отдельные values и манифесты-заготовки. Перед использованием Argo CD нужно заменить `repoURL` в application manifests на реальный GitLab-репозиторий.

DNS-план для реального домена вынесен в [deploy/eks/DNS.md](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/deploy/eks/DNS.md). Для Reg.Cloud добавлен отдельный профиль [charts/prizma/values-regcloud.yaml](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/charts/prizma/values-regcloud.yaml) и заметки [deploy/regcloud/README.md](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/deploy/regcloud/README.md).

## Kubernetes и observability

Helm chart поднимает:

- API deployment
- worker deployment
- MinIO
- RabbitMQ
- Triton scaffold
- shared state PVC
- readiness/liveness probes
- HPA и `ServiceMonitor`
- optional Argo Rollouts canary with Prometheus analysis
- artifact retention CronJob
- runtime secret integration through generated Secret, existing Secret or ExternalSecret

Отдельно есть минимальные Kubernetes-манифесты для Prometheus и Grafana с:

- scrape `/metrics`
- pre-provisioned datasource
- preloaded dashboard `Prizma Overview`
- базовыми alert rules для error rate, latency и stuck jobs

## MLOps и эксплуатация

Локальный MLOps gate:

```bash
make mlops
```

Он генерирует synthetic golden set, metadata baseline, benchmark, drift report и model card:

- [dvc.yaml](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/dvc.yaml)
- [params.yaml](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/params.yaml)
- [docs/mlops/model-card.md](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/docs/mlops/model-card.md)

Эксплуатационные документы:

- [docs/security/threat-model.md](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/docs/security/threat-model.md)
- [docs/runbooks/retraining.md](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/docs/runbooks/retraining.md)
- [docs/runbooks/rollback.md](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/docs/runbooks/rollback.md)
- [docs/runbooks/incident-response.md](/Users/sanalpernyaev/Downloads/Новая%20папка/Разработка%20ПО/docs/runbooks/incident-response.md)

Локальные проверки перед commit:

```bash
make lint
make test
make security
make mlops
make kube-validate
```

## Ограничения минимального контура

- shared state хранится в файловом job repository, поэтому в managed Kubernetes нужен RWX storage
- Triton model repository сейчас scaffold, а не production-модель
- production profiles expect an existing `prizma-runtime-overrides` Secret or ExternalSecret-backed Secret
- MLflow logging в baseline включается автоматически только если пакет `mlflow` установлен в среде

Это production-oriented baseline, который покрывает backend, broker/storage, CI/CD, MLOps governance, observability и Kubernetes-контур из кейса.
