# Project Status

Last Updated: 2026-07-11

---

# Current Phase

Phase 4 — Embeddings and Retrieval

---

# Current Milestone

M4.1 — pgvector Setup

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

## Phase 2 — Candidate Evidence Model (Complete)

### M2.1 — Evidence Schema

- `CandidateEvidence` SQLAlchemy model (`app/models/evidence.py`) + Pydantic read schema
  (`app/schemas/evidence.py`) with `EvidenceType` (`experience_bullet`, `project_bullet`,
  `achievement`, `skill`, `certification`, `education_item`) and `SourceEntityType` enums.
  Provenance via `source_entity_type`/`source_entity_id`; free-form `evidence_metadata`
  (Postgres `JSONB`). Migration `0f9ff0d35f97_create_candidate_evidence_table.py`.

### M2.2 — Evidence Generation

- `app/services/evidence_service.py::generate_evidence` — pure, deterministic function
  (no LLM, no DB access; unit tested directly on plain ORM objects per NFR-003) producing
  one evidence unit per atomic claim: experience/project description + each achievement,
  one per skill, one per education entry (+ its achievements), one per certification.
  Wired into `profile_persistence.py` so evidence is generated and committed atomically
  alongside the candidate profile on upload.

### M2.3 — Evidence API

- `GET /api/v1/candidate-profiles/{candidate_profile_id}/evidence` lists evidence
  ordered by creation; `404 NOT_FOUND` for an unknown profile.

### Phase 2 Exit Criteria — Verified

Candidate claims are represented as traceable, inspectable evidence units. Confirmed via
25 automated tests (`make test`), Ruff/mypy clean, and a live end-to-end run (real Ollama
+ real Postgres) inspecting the evidence API response directly. Note: evidence generation
correctly produces **no** fabricated evidence when the upstream LLM extraction leaves a
field empty (observed live — a bullet under one experience wasn't extracted by the small
local model that run, and no evidence was invented to compensate), confirming the
generator defers faithfully to whatever was actually captured upstream.

## Phase 3 — Job Description Intelligence (Complete)

### M3.1 — Job Submission

- `POST /api/v1/jobs` accepts `{"text": "..."}`; blank/missing text rejected with
  `422 VALIDATION_ERROR` via a new global `RequestValidationError` handler
  (`app/main.py`) that normalizes FastAPI's default validation errors into the same
  `{"error": {"code", "message"}}` envelope used elsewhere.
- `JobDescription`/`JobRequirement` SQLAlchemy models (`app/models/job.py`); source
  text preserved verbatim. Migration
  `2badee0172d6_create_job_description_and_job_.py`.

### M3.2 — Requirement Extraction

- Versioned prompt (`app/prompts/jd_extraction.md`, `v1`) and `JobRequirementExtraction`
  schema (`app/schemas/job.py`); `app/services/jd_analyzer.py` mirrors the resume
  extraction pattern (LLMClient + bounded retries + schema validation).

### M3.3 — Requirement Classification

- Each `JobRequirementItem` carries `category` (`skill`, `experience`,
  `responsibility`, `education`, `certification`, `domain_knowledge`) and `importance`
  (`required`, `preferred`, `optional`), assigned by the LLM per explicit prompt rules
  distinguishing "must have"/"Requirements" language from "nice to have"/"Preferred"
  language, and persisted as-is (no separate deterministic reclassification pass).

### Phase 3 Exit Criteria — Verified

A real job description produces validated, persisted structured requirements.
Confirmed via 29 automated tests (`make test`), Ruff/mypy clean, and a live end-to-end
run (real Ollama + real Postgres) against a realistic ML engineer job posting: role
title, company, and seniority were extracted correctly, and all 7 requirements were
classified into the correct category and required-vs-preferred importance matching the
source text's "Requirements"/"Preferred" sections exactly, with no fabricated
requirements. **Observation**: the two "Responsibilities" bullets in that same posting
were not extracted as `responsibility`-category requirements by the small local model
used — a prompt/extraction-quality nuance to revisit during Phase 9 evaluation, not a
functional defect (schema validation, categorization, and persistence all behaved
correctly for what was extracted).

**Bug found and fixed during this phase**: `AsyncSession.refresh()` without
`attribute_names` expires relationships as well as columns; the first access of a
relationship (e.g. `JobDescription.requirements`) during Pydantic
`from_attributes` serialization after such a refresh raised `MissingGreenlet` (an
async-unsafe lazy load). Fixed in both `job_persistence.py` and
`profile_persistence.py` by scoping the refresh to `attribute_names=["created_at"]`
(the only server-generated column actually needed).

---

# In Progress

- None. Phases 0–3 are complete. Phase 4 (Embeddings and Retrieval) has not yet
  started.

---

# Not Started

## Phase 4 — Embeddings and Retrieval

- M4.1 — pgvector Setup
- M4.2 — Embedding Service
- M4.3 — Evidence Indexing
- M4.4 — Semantic Retrieval
- M4.5 — Retrieval Evaluation

## Later Phases

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

- `backend/app/api/{analysis,generation}.py`
- `backend/app/models/application.py` (Phase 7+)
- `backend/app/schemas/{matching,generation}.py`
- `backend/app/services/{matching_service,scoring_service,retrieval_service,
  embedding_service,tailoring_service}.py`
- `backend/app/prompts/{evidence_matching,bullet_rewriting}.md`
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

Begin Phase 4 — Embeddings and Retrieval, starting with M4.1 (pgvector Setup): enable
the pgvector extension and add embedding storage for candidate evidence.
