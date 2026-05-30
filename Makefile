PYTHON ?= python3

.PHONY: install run test lint compose-up compose-down helm-template kube-validate

install:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install -e .[dev]

run:
	uvicorn prizma_backend.main:app --app-dir src --reload

test:
	pytest -q

lint:
	ruff check src tests
	ruff format --check src tests

compose-up:
	docker compose -p prizma up -d --build

compose-down:
	docker compose -p prizma down -v

helm-template:
	docker run --rm -v "$$PWD":/work -w /work alpine/helm:3.16.4 template prizma charts/prizma -f charts/prizma/values-dev.yaml

kube-validate:
	./.tools/kubeconform -strict -ignore-missing-schemas -summary deploy/k8s/observability/*.yaml
