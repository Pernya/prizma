PYTHON ?= python3
PYTHONPATH ?= src
HELM ?= ./.tools/helm
KUBECONFORM ?= ./.tools/kubeconform
KUBE_VALIDATE_DIR ?= /tmp/prizma-kubeconform

.PHONY: install run test lint security mlops smoke compose-up compose-down helm-template kube-validate cleanup

install:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install -e .[dev]

run:
	uvicorn prizma_backend.main:app --app-dir src --reload

test:
	pytest -q

lint:
	ruff check src tests scripts
	ruff format --check src tests scripts

security:
	pip-audit --progress-spinner=off
	bandit -r src scripts -q
	python scripts/security/check_detect_secrets.py

mlops:
	PYTHONPATH=$(PYTHONPATH) python scripts/mlops/prepare_golden_set.py --params params.yaml --output data/golden/input
	PYTHONPATH=$(PYTHONPATH) python scripts/mlops/train_baseline.py --params params.yaml --output models/prizma_stylizer/metadata.json
	PYTHONPATH=$(PYTHONPATH) python scripts/mlops/evaluate_model.py --params params.yaml --input data/golden/input --model models/prizma_stylizer/metadata.json --output reports/mlops/benchmark.json
	PYTHONPATH=$(PYTHONPATH) python scripts/mlops/drift_report.py --params params.yaml --baseline data/golden/input --current data/monitoring/input --output reports/mlops/drift.json
	PYTHONPATH=$(PYTHONPATH) python scripts/mlops/generate_model_card.py --params params.yaml --model models/prizma_stylizer/metadata.json --benchmark reports/mlops/benchmark.json --drift reports/mlops/drift.json --output docs/mlops/model-card.md

smoke:
	PYTHONPATH=$(PYTHONPATH) python scripts/smoke/e2e_job.py --base-url http://localhost:8000

cleanup:
	PYTHONPATH=$(PYTHONPATH) python scripts/ops/cleanup_artifacts.py --dry-run

compose-up:
	docker compose -p prizma up -d --build

compose-down:
	docker compose -p prizma down -v

helm-template:
	$(HELM) template prizma charts/prizma -f charts/prizma/values-dev.yaml

kube-validate:
	mkdir -p $(KUBE_VALIDATE_DIR)
	$(HELM) template prizma charts/prizma -f charts/prizma/values-dev.yaml > $(KUBE_VALIDATE_DIR)/dev.yaml
	$(HELM) template prizma charts/prizma -f charts/prizma/values-prod.yaml > $(KUBE_VALIDATE_DIR)/prod.yaml
	$(HELM) template prizma charts/prizma -f charts/prizma/values-eks.yaml > $(KUBE_VALIDATE_DIR)/eks.yaml
	$(HELM) template prizma charts/prizma -f charts/prizma/values-regcloud.yaml > $(KUBE_VALIDATE_DIR)/regcloud.yaml
	$(HELM) template prizma charts/prizma --set rollouts.enabled=true --set serviceMonitor.enabled=true > $(KUBE_VALIDATE_DIR)/rollout.yaml
	$(KUBECONFORM) -strict -ignore-missing-schemas -summary $(KUBE_VALIDATE_DIR)/*.yaml deploy/k8s/observability/*.yaml deploy/argocd/*.yaml
