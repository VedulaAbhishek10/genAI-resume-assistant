# GenAI Resume Assistant

An evidence-grounded GenAI application that helps users tailor resumes to target job
descriptions using a reusable candidate profile. See `docs/PROJECT_SPEC.md` for the full
product specification and `docs/ROADMAP.md` for the development plan.

The project is under active, incremental development. Current status: `docs/STATUS.md`.

## Requirements

- Python 3.14 (`>=3.14,<3.15`)
- Docker (for the local PostgreSQL database)
- [Ollama](https://ollama.com) running locally with a pulled model (for structured resume
  extraction)

## Setup

```bash
make install
```

This creates a `.venv` virtual environment at the repository root and installs the backend
package with its development dependencies.

Copy the environment template and adjust as needed (in particular `OLLAMA_MODEL`, to match
a model you have pulled locally via `ollama pull <model>`):

```bash
cp .env.example .env
```

Start the database (runs on host port `5433` to avoid clashing with any existing local
PostgreSQL install) and apply migrations:

```bash
make db-up
make migrate
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

Upload a resume (PDF or DOCX) and receive extracted text plus a structured, evidence-grounded
candidate profile (this also computes embeddings for each evidence unit; the first call
downloads the embedding model from Hugging Face and may take longer):

```bash
curl -F "file=@/path/to/resume.pdf;type=application/pdf" http://127.0.0.1:8000/api/v1/resumes
```

Retrieve the evidence semantically closest to a job requirement:

```bash
curl -G "http://127.0.0.1:8000/api/v1/candidate-profiles/<candidate_profile_id>/retrieve" \
  --data-urlencode "query=Experience with backend web frameworks"
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

## Database Migrations

Schema changes are managed with Alembic from `backend/`:

```bash
cd backend && ../.venv/bin/alembic revision --autogenerate -m "describe the change"
cd backend && ../.venv/bin/alembic upgrade head
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
