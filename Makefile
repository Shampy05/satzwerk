.DEFAUL_GOAL := help

.PHONY: help sync lock add add-dev lint format format-check typecheck test coverage check clean build run

help: ## show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'

# ---- Setup ----

sync: ## Install/sync all deps (incl. dev) from uv.lock, creating .venv if needed
	uv sync --all-extras --dev

lock: ## Re-resolve dependencies and update uv.lock
	uv lock

add: ## Add a runtime dependency: make add pkg=requests
	uv add ${pkg}

add-dev: ## Add a dev dependency: make add-dev pkg=requests
	uv add --dev ${pkg}

# ---- Code quality ----

lint: ## Check code style and lint errors with ruff
	uv run ruff check .

format: ## Auto-format and auto-fix with ruff
	uv run ruff format .
	uv run ruff check --fix .

format-check: ## Check formatting without modifying files (for CI)
	uv run ruff format --check .

typecheck: ## Run pyright
	uv run pyright

# ---- Housekeeping ----

clean: ## Remove caches and build artifacts (keeps .venv)
	rm -rf build dist *.egg-info
	rm -rf .pytest-cache .ruff_cache .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +

# ---- Development server ----

dev: ## Run the FastAPI server in development mode with hot-reloading
	uv run uvicorn src.main:app --reload --port 8000

# ---- Infrastructure ----

up: ## Start the local PostgreSQL and Valkey containers in the background
	docker compose up -d

down: ## Stop and remove the local containers
	docker compose down

# ---- Database migrations ----

migrate: ## Generate a new Alembic migration (usage: make migrate m="added chunk table")
	uv run alembic revision --autogenerate -m "$(m)"

upgrade: ## Apply all pending database migrations to the database
	uv run alembic upgrade head

# ---- Testing ----

test: ## Run the pytest suite
	uv run pytest
