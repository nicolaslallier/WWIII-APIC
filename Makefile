.PHONY: help install lint format format-check type-check test test-unit test-integration test-e2e coverage clean docker-build docker-up docker-down docker-test ci cd quality-gates pre-commit-install pre-commit-run git-status git-commit git-commit-feat git-commit-fix git-commit-refactor git-push git-push-upstream git-pr-create git-pr-create-auto git-commit-push git-commit-push-pr

# Variables
PYTHON := python3.12
UV := uv
DOCKER_COMPOSE := docker-compose
APP_NAME := wwiii-apic
IMAGE_NAME := $(APP_NAME):latest

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using uv
	$(UV) pip install -e ".[dev,test]"

lint: ## Run ruff linter
	$(UV) run ruff check app tests

format: ## Format code with black and ruff
	$(UV) run black app tests
	$(UV) run ruff format app tests

format-check: ## Check code formatting
	$(UV) run black --check app tests
	$(UV) run ruff format --check app tests

type-check: ## Run mypy type checker
	$(UV) run mypy app

test: ## Run all tests
	$(UV) run pytest

test-unit: ## Run unit tests only
	$(UV) run pytest tests/unit -m unit

test-integration: ## Run integration tests only
	$(UV) run pytest tests/integration -m integration

test-e2e: ## Run e2e tests only
	$(UV) run pytest tests/e2e -m e2e

coverage: ## Run tests with coverage report
	$(UV) run pytest --cov=app --cov-report=html --cov-report=term-missing

clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov dist build

docker-build: ## Build Docker image
	docker build -t $(IMAGE_NAME) .

docker-up: ## Start Docker Compose services
	$(DOCKER_COMPOSE) up -d

docker-down: ## Stop Docker Compose services
	$(DOCKER_COMPOSE) down

docker-test: ## Run tests in Docker container
	docker run --rm $(IMAGE_NAME) pytest

quality-gates: ## Run all quality gates (lint, format-check, type-check, test)
	@echo "Running quality gates..."
	@$(MAKE) lint
	@$(MAKE) format-check
	@$(MAKE) type-check
	@$(MAKE) test
	@echo "All quality gates passed!"

ci: ## Run CI pipeline
	@echo "Starting CI pipeline..."
	@./scripts/ci.sh

cd: ## Run CD pipeline
	@echo "Starting CD pipeline..."
	@./scripts/cd.sh

pre-commit-install: ## Install pre-commit hooks
	$(UV) run pre-commit install

pre-commit-run: ## Run pre-commit hooks on all files
	$(UV) run pre-commit run --all-files

# Git workflow commands
git-status: ## Show git status
	git status

git-commit: ## Commit changes (usage: make git-commit MSG="your message")
	git add -A
	git commit -m "$(MSG)"

git-commit-feat: ## Commit feature (usage: make git-commit-feat MSG="your message")
	git add -A
	git commit -m "feat: $(MSG)"

git-commit-fix: ## Commit fix (usage: make git-commit-fix MSG="your message")
	git add -A
	git commit -m "fix: $(MSG)"

git-commit-refactor: ## Commit refactor (usage: make git-commit-refactor MSG="your message")
	git add -A
	git commit -m "refactor: $(MSG)"

git-push: ## Push current branch to origin
	git push origin $$(git branch --show-current)

git-push-upstream: ## Push and set upstream
	git push -u origin $$(git branch --show-current)

git-pr-create: ## Create PR (requires gh CLI, usage: make git-pr-create TITLE="title" BODY="body")
	gh pr create --title "$(TITLE)" --body "$(BODY)" --base main

git-pr-create-auto: ## Create PR from last commit message
	gh pr create --title "$$(git log -1 --pretty=%B)" --body "## Changes\n\n$$(git log origin/main..HEAD --pretty='- %s')\n\n## Testing\n\n- [ ] Tests pass\n- [ ] Quality gates pass" --base main

git-commit-push: ## Commit and push (usage: make git-commit-push MSG="your message")
	git add -A
	git commit -m "$(MSG)"
	git push origin $$(git branch --show-current)

git-commit-push-pr: ## Commit, push, and create PR (usage: make git-commit-push-pr MSG="your message")
	git add -A
	git commit -m "$(MSG)"
	git push -u origin $$(git branch --show-current)
	gh pr create --title "$$(git log -1 --pretty=%B)" --body "## Changes\n\n$$(git log origin/main..HEAD --pretty='- %s')\n\n## Testing\n\n- [ ] Tests pass\n- [ ] Quality gates pass" --base main

