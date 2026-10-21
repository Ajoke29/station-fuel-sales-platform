# Common tasks. Run `make help` to see them all.

IMAGE        ?= ghcr.io/ajoke29/station-fuel-sales-platform
TAG          ?= main
CLUSTER      ?= fuel-sales
NAMESPACE    ?= fuel-sales-dev
RELEASE      ?= station-fuel-sales
CHART        := helm/station-fuel-sales
TF_DIR       := infra/terraform/azure
VENV         := .venv
PY           := $(VENV)/bin/python

.DEFAULT_GOAL := help
.PHONY: help venv test run lint lint-yaml lint-docker lint-helm lint-tf monitoring-test \
        docker-build docker-run docker-stop scan kind-up kind-load deploy-dev kind-down \
        tf-validate clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

venv: ## Create a Python virtual environment with dev dependencies
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q -r app/requirements-dev.txt yamllint==1.38.0 pyyaml

test: ## Run unit tests
	cd app && ../$(VENV)/bin/pytest -v

run: ## Run the app locally on http://localhost:8000 (no Docker)
	cd app && ../$(VENV)/bin/uvicorn fuel_sales.main:app --reload --port 8000

lint: lint-yaml lint-docker lint-helm lint-tf monitoring-test ## Run every linter

lint-yaml: ## yamllint all YAML
	$(VENV)/bin/yamllint -s .

lint-docker: ## hadolint the Dockerfile
	hadolint app/Dockerfile

lint-helm: ## helm lint + template with dev and prod values
	@for env in dev prod; do \
	  helm lint $(CHART) -f $(CHART)/values-$$env.yaml && \
	  helm template sfs $(CHART) -f $(CHART)/values-$$env.yaml > /dev/null || exit 1; \
	done

lint-tf: tf-validate ## terraform fmt + validate

tf-validate: ## terraform fmt -check and validate (no Azure account needed)
	cd $(TF_DIR) && terraform fmt -check -recursive && terraform init -backend=false -input=false >/dev/null && terraform validate

monitoring-test: ## Check and unit-test the Prometheus alert rules
	@mkdir -p build
	$(PY) scripts/extract-rules.py monitoring/prometheus-rules.yaml build/rules.yaml
	promtool check rules build/rules.yaml
	promtool test rules monitoring/tests/alerts-test.yaml

docker-build: ## Build the container image
	docker build -t $(IMAGE):$(TAG) app

docker-run: ## Run the container on http://localhost:8080 (read-only, no root)
	docker run -d --rm --name fuel-sales --read-only --tmpfs /tmp --cap-drop ALL \
	  --security-opt no-new-privileges -p 8080:8000 $(IMAGE):$(TAG)
	@echo "Open http://localhost:8080"

docker-stop: ## Stop the local container
	-docker stop fuel-sales

scan: ## Trivy scan of the repo and the image
	trivy fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL --ignore-unfixed .
	trivy image --severity HIGH,CRITICAL --ignore-unfixed $(IMAGE):$(TAG)

kind-up: ## Create the local kind cluster (1 control plane + 2 workers)
	kind create cluster --config k8s/kind-cluster.yaml

kind-load: docker-build ## Build the image and load it into kind
	kind load docker-image $(IMAGE):$(TAG) --name $(CLUSTER)

deploy-dev: kind-load ## Deploy to kind with Helm (dev values) -> http://localhost:8080
	helm upgrade --install $(RELEASE) $(CHART) -f $(CHART)/values-dev.yaml \
	  -n $(NAMESPACE) --create-namespace --wait --timeout 3m
	kubectl -n $(NAMESPACE) get pods,svc

kind-down: ## Delete the local kind cluster
	kind delete cluster --name $(CLUSTER)

clean: ## Remove build artefacts and caches
	rm -rf build $(VENV) app/.pytest_cache app/test-results.xml $(TF_DIR)/.terraform
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
