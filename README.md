# GenAI Resume Assistant

An evidence-grounded GenAI application that helps users tailor resumes to target job
descriptions using a reusable candidate profile. See `docs/PROJECT_SPEC.md` for the full
product specification and `docs/ROADMAP.md` for the development plan.

The project is under active, incremental development. Current status: `docs/STATUS.md`.

## Requirements

- Python 3.14 (`>=3.14,<3.15`)

## Setup

```bash
make install
```

This creates a `.venv` virtual environment at the repository root and installs the backend
package with its development dependencies.

Copy the environment template and adjust as needed:

```bash
cp .env.example .env
```

## Running the backend

```bash
make run
```

Starts the FastAPI development server with auto-reload at `http://127.0.0.1:8000`.
Verify it is running:

```bash
curl http://127.0.0.1:8000/health
```

## Testing

```bash
make test
```

## Linting and Type Checking

```bash
make lint
make typecheck
```

Run everything (lint, typecheck, test) with:

```bash
make check
```

## Project Structure

```text
backend/   FastAPI application (API, domain services, AI integration, persistence)
frontend/  React application
docs/      Product, architecture, and process documentation
data/      Local sample/evaluation data (not committed; see .gitignore)
```

## Documentation

Start with `CLAUDE.md` for the mandatory reading order, then:

- `docs/PROJECT_SPEC.md` — product specification
- `docs/REQUIREMENTS.md` — functional and non-functional requirements
- `docs/ARCHITECTURE.md` — system architecture
- `docs/AI_SYSTEM.md` — AI/LLM system design
- `docs/DATA_MODEL.md` — domain and data model
- `docs/ROADMAP.md` — phased development roadmap
- `docs/STATUS.md` — current implementation status
- `docs/DECISIONS.md` — architecture decision records
