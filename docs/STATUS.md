# Project Status

Last Updated: 2026-07-11

---

# Current Phase

Phase 2 — Candidate Evidence Model

---

# Current Milestone

M2.1 — Evidence Schema

---

# Overall Status

IN PROGRESS

---

# Completed

## Phase 0 — Repository and Development Environment (Complete)

- Project directory and repository structure created.
- Git repository initialized; `main` branch configured.
- Python 3.14.6 development environment verified via `.venv` at the repository root.
- `CLAUDE.md` and `.env` ignored by Git; `.gitignore` covers Python, virtualenv, IDE,
  and private data artifacts.
- `.env.example` documents configurable application, LLM provider, embedding, and
  database settings.
- Core project documentation populated (`docs/PROJECT_SPEC.md`, `docs/REQUIREMENTS.md`,
  `docs/ARCHITECTURE.md`, `docs/AI_SYSTEM.md`, `docs/DATA_MODEL.md`, `docs/ROADMAP.md`,
  `docs/DECISIONS.md`, `docs/EVALUATION.md`, `docs/API.md`).
- `backend/pyproject.toml` configured: Python `>=3.14,<3.15` constraint, Ruff config
  (`target-version = "py314"`), mypy config (`python_version = "3.14"`, strict mode),
  pytest config.
- Minimal FastAPI application: `app/core/config.py` (`Settings` via pydantic-settings),
  `app/core/logging.py`, `app/main.py` (`GET /health`).
- Developer commands documented via root `Makefile` and `README.md`.

### Phase 0 Exit Criteria — Verified

- Application starts, health endpoint responds, tests/lint/typecheck all pass.
  Setup documented in `README.md` and `Makefile`.

---

## Phase 1 — Resume Ingestion (Complete)

### M1.1 — Upload API

- `POST /api/v1/resumes` accepts multipart PDF/DOCX uploads.
- Validation (`app/services/storage_service.py`): extension allowlist, magic-byte
  signature check (rejects mislabeled/corrupt files), empty-file rejection, configurable
  size limit (`MAX_UPLOAD_SIZE_MB`).
- Controlled error taxonomy (`app/core/exceptions.py` + global `AppError` handler in
  `app/main.py`): `UNSUPPORTED_FILE_TYPE` (415), `EMPTY_FILE` (400), `FILE_TOO_LARGE`
  (413), `INVALID_DOCUMENT` (400).
- Original file bytes are stored under `UPLOAD_STORAGE_DIR/<resume_id>/original.<ext>`.

### M1.2 — Document Extraction

- `app/services/document_parser.py`: PyMuPDF (`fitz`) for PDF, `python-docx` for DOCX,
  shared whitespace/newline normalization. Raises `ExtractionError` (422) on failure
  (encrypted/corrupt documents, no extractable text).
- Extracted text is preserved separately from the original file
  (`UPLOAD_STORAGE_DIR/<resume_id>/extracted.txt`), satisfying FR-002's provenance
  requirement.

### M1.3 — Resume Structured Extraction

- `LLMClient` abstraction (`app/llm/base.py`) per `docs/AI_SYSTEM.md`; `OllamaClient`
  implementation (`app/llm/ollama.py`) using bounded-retry structured generation
  (`format` = JSON schema, max 2 attempts) that raises `LLMValidationError` (422) on
  persistent invalid output and `LLMProviderError` (502) on transport failure.
- Candidate profile schema (`app/schemas/resume.py`: `CandidateProfileExtraction` with
  experiences/projects/skills/education/certifications).
- Versioned extraction prompt (`app/prompts/resume_extraction.md`, `v1`) with explicit
  grounding rules and prohibited-fabrication instructions per `docs/AI_SYSTEM.md`.
- Verified against a live local Ollama model (not just mocks): grounded extraction
  correctly leaves unstated fields (`description`, `field_of_study`, etc.) null rather
  than fabricating values.
- **Implementation note**: Ollama "thinking" models (e.g. Qwen3) emit structured JSON
  into a `thinking` response field rather than `response`; the Ollama client sends
  `"think": false` and falls back to `thinking` defensively. Documented in
  `docs/AI_SYSTEM.md`.

### M1.4 — Candidate Profile Persistence

- PostgreSQL via `docker-compose.yml` (`postgres:16`, host port `5433` to avoid
  colliding with any existing local PostgreSQL instance — see ADR-011).
- SQLAlchemy 2.0 async models (`app/models/candidate.py`, `app/models/resume.py`):
  `CandidateProfile`, `Experience`, `Project`, `Skill`, `Education`, `Certification`,
  `Resume`, using the psycopg3 dialect for both the async application engine
  (`app/db/session.py`) and the synchronous Alembic migration engine (ADR-011).
  Achievement/technology lists use Postgres `ARRAY` columns rather than separate
  join tables.
- Alembic initialized (`backend/alembic/`); initial migration
  (`0bf489162195_create_candidate_profile_and_resume_.py`) creates all seven tables.
  Verified reproducible via `alembic downgrade base` → `alembic upgrade head` and
  `alembic check` (no drift against current models).
- `app/services/profile_persistence.py` persists the extracted `CandidateProfile` and
  `Resume` together on upload.
- Verified end-to-end against a live Ollama model and the real Postgres container
  (not mocks): uploaded resume produced correct rows in `resumes` and
  `candidate_profiles` (and child tables), confirmed via direct SQL query.

### Phase 1 Exit Criteria — Verified

A supported resume (PDF or DOCX) can be uploaded and converted into a validated,
persisted structured candidate profile. Confirmed via:

- 20 automated tests passing (`make test`), including a dedicated persistence
  integration test (`tests/integration/test_candidate_profile_persistence.py`) that
  queries the real database after an upload.
- Ruff and mypy (strict) clean (`make lint`, `make typecheck`).
- Two independent live end-to-end runs (DOCX and PDF fixtures) against the actual
  local Ollama server and actual Postgres container, with results inspected via
  direct SQL.

---

# In Progress

- None. Phase 1 is complete. Phase 2 (Candidate Evidence Model) has not yet started.

---

# Not Started

## Phase 2 — Candidate Evidence Model

- M2.1 — Evidence Schema
- M2.2 — Evidence Generation
- M2.3 — Evidence API

## Later Phases

- Phase 3 — Job Description Intelligence
- Phase 4 — Embeddings and Retrieval
- Phase 5 — Matching and Scoring
- Phase 6 — Grounded Resume Tailoring
- Phase 7 — Resume Versioning and Export
- Phase 8 — Frontend Product Experience
- Phase 9 — Evaluation and Observability
- Phase 10 — Production Hardening

---

# Notes on Existing Scaffolding

The repository still contains empty placeholder files for later phases, created ahead
of implementation to reflect the intended structure from `docs/ARCHITECTURE.md`:

- `backend/app/api/{jobs,analysis,generation}.py`
- `backend/app/llm/provider.py` — implemented; `app/models/{job,application}.py` — not
  yet implemented (Phase 3 / Phase 7+)
- `backend/app/schemas/{job,matching,generation}.py`
- `backend/app/services/{jd_analyzer,matching_service,scoring_service,retrieval_service,
  embedding_service,tailoring_service}.py`
- `backend/app/prompts/{jd_extraction,evidence_matching,bullet_rewriting}.md`
- `backend/tests/evaluation/`
- `frontend/src/**`

These remain intentionally unimplemented (empty) and are out of scope until their
corresponding roadmap milestone begins.

`backend/Dockerfile` remains an empty placeholder, deferred to Phase 10 (M10.3
containerization) — the application itself is not yet containerized; only its
PostgreSQL dependency runs in Docker during local development.

---

# Known Blockers

None currently.

---

# Next Action

Begin Phase 2 — Candidate Evidence Model, starting with M2.1 (Evidence Schema):
define evidence types, source references, and provenance for candidate evidence
units, per `docs/DATA_MODEL.md`'s `CandidateEvidence` entity.
