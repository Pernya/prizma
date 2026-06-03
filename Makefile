PYTHON ?= python3
VENV_PYTHON := .venv/bin/python
RUN_PYTHON = $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),$(PYTHON))
PYTHONPATH ?= src
HELM ?= ./.tools/helm
KUBECONFORM ?= ./.tools/kubeconform
KUBE_VALIDATE_DIR ?= /tmp/prizma-kubeconform

.PHONY: install run test lint security contract mlops smoke compose-up compose-down helm-template kube-validate cleanup

install:
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install -e ".[dev]"

run:
	$(RUN_PYTHON) -m uvicorn prizma_backend.main:app --app-dir src --reload

test:
	$(RUN_PYTHON) -m pytest -q

lint:
	$(RUN_PYTHON) -m ruff check src tests scripts
	$(RUN_PYTHON) -m ruff format --check src tests scripts

security:
	$(RUN_PYTHON) -m pip_audit --progress-spinner=off
	$(RUN_PYTHON) -m bandit -r src scripts -q
	$(RUN_PYTHON) scripts/security/check_detect_secrets.py

contract:
	PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) scripts/contracts/export_openapi.py --output docs/api/openapi.json

mlops:
	PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) scripts/mlops/prepare_golden_set.py --params params.yaml --output data/golden/input
	PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) scripts/mlops/validate_dataset.py --params params.yaml --input data/golden/input --output reports/mlops/data-validation.json
	PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) scripts/mlops/train_baseline.py --params params.yaml --output models/prizma_stylizer/metadata.json
	PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) scripts/mlops/evaluate_model.py --params params.yaml --input data/golden/input --model models/prizma_stylizer/metadata.json --output reports/mlops/benchmark.json
	PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) scripts/mlops/drift_report.py --params params.yaml --baseline data/golden/input --current data/monitoring/input --output reports/mlops/drift.json
	PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) scripts/mlops/generate_model_card.py --params params.yaml --model models/prizma_stylizer/metadata.json --benchmark reports/mlops/benchmark.json --drift reports/mlops/drift.json --output docs/mlops/model-card.md

smoke:
	PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) scripts/smoke/e2e_job.py --base-url http://localhost:8000

cleanup:
	PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) scripts/ops/cleanup_artifacts.py --dry-run

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
	$(HELM) template prizma charts/prizma --set secrets.external.enabled=true --set secrets.create=false --set secrets.existingSecret=prizma-runtime-overrides > $(KUBE_VALIDATE_DIR)/external-secret.yaml
	$(KUBECONFORM) -strict -ignore-missing-schemas -summary $(KUBE_VALIDATE_DIR)/*.yaml deploy/k8s/observability/*.yaml deploy/argocd/*.yaml
