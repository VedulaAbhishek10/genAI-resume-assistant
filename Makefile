VENV := .venv
PYTHON := $(VENV)/bin/python
UVICORN := $(VENV)/bin/uvicorn

.PHONY: venv install run test lint format typecheck check db-up db-down migrate \
	frontend-install frontend-dev frontend-build frontend-lint

venv:
	python3.14 -m venv $(VENV)

install: venv
	$(VENV)/bin/pip install -e "./backend[dev]"

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

migrate:
	cd backend && ../$(PYTHON) -m alembic upgrade head

run:
	cd backend && ../$(UVICORN) app.main:app --reload

test:
	cd backend && ../$(PYTHON) -m pytest

lint:
	cd backend && ../$(PYTHON) -m ruff check .

format:
	cd backend && ../$(PYTHON) -m ruff format .

typecheck:
	cd backend && ../$(PYTHON) -m mypy app

check: lint typecheck test

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

frontend-lint:
	cd frontend && npm run lint
