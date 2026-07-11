VENV := .venv
PYTHON := $(VENV)/bin/python
UVICORN := $(VENV)/bin/uvicorn

.PHONY: venv install run test lint format typecheck check

venv:
	python3.14 -m venv $(VENV)

install: venv
	$(VENV)/bin/pip install -e "./backend[dev]"

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
