# Development Roadmap

## Development Strategy

The project is implemented incrementally.

Each phase contains milestones.

A milestone is complete only when:

- required functionality is implemented,
- relevant tests exist,
- validation passes,
- acceptance criteria are satisfied,
- documentation is updated,
- `docs/STATUS.md` reflects the actual state.

Do not implement future phases prematurely.

---

# Phase 0 — Repository and Development Environment

## Goal

Establish a reproducible development foundation.

---

## M0.1 — Repository Structure

### Scope

- establish documented repository structure,
- configure `.gitignore`,
- create `.env.example`,
- verify local virtual environment,
- establish Python version policy,
- create project documentation.

### Acceptance Criteria

- repository structure exists,
- Python 3.14 virtual environment is usable,
- `CLAUDE.md` is ignored by Git,
- `.env` is ignored by Git,
- required documentation files exist,
- `docs/STATUS.md` reflects the actual repository state.

---

## M0.2 — Python Project Configuration

### Scope

- configure `backend/pyproject.toml`,
- define Python version constraint,
- add minimal backend dependencies,
- configure Ruff,
- configure mypy,
- configure pytest.

### Acceptance Criteria

- project dependencies can be installed,
- Ruff configuration exists,
- mypy configuration exists,
- pytest configuration exists,
- basic validation commands execute successfully.

---

## M0.3 — Minimal Backend

### Scope

- create FastAPI application,
- create health endpoint,
- configure application settings,
- configure initial logging,
- add initial tests.

### Acceptance Criteria

- application starts,
- health endpoint returns a successful response,
- configuration loads correctly,
- relevant tests pass.

---

## M0.4 — Developer Commands

### Scope

- configure Makefile or equivalent commands,
- document local setup,
- document test commands,
- document lint commands,
- document type-check commands.

### Acceptance Criteria

- common developer commands are documented,
- application can be started using documented instructions,
- tests can be run using documented instructions,
- Phase 0 exit criteria are satisfied.

---

## Phase 0 Exit Criteria

- application starts,
- health endpoint responds,
- tests pass,
- linting passes,
- type checks pass,
- setup is documented.

---

# Phase 1 — Resume Ingestion

## Goal

Accept resume documents and extract usable content.

---

## M1.1 — Upload API

### Scope

- PDF support,
- DOCX support,
- file validation,
- size limits,
- safe filename handling,
- controlled errors.

### Acceptance Criteria

- valid PDF and DOCX uploads are accepted,
- unsupported files are rejected,
- oversized files are rejected,
- invalid uploads return controlled errors.

---

## M1.2 — Document Extraction

### Scope

- PyMuPDF PDF extraction,
- python-docx DOCX extraction,
- normalized text output.

### Acceptance Criteria

- supported documents produce extracted text,
- extraction failures return controlled errors,
- document parsing logic has relevant tests.

---

## M1.3 — Resume Structured Extraction

### Scope

- define Pydantic schemas,
- create resume extraction prompt,
- implement structured LLM extraction,
- validate model outputs.

### Acceptance Criteria

- extracted resume text can produce a validated candidate profile,
- invalid LLM output does not silently enter application state,
- AI provider failures are handled.

---

## M1.4 — Candidate Profile Persistence

### Scope

- database integration,
- SQLAlchemy models,
- Alembic migration,
- persist normalized candidate profile.

### Acceptance Criteria

- candidate profiles can be persisted,
- database migrations are reproducible,
- relevant integration tests pass.

---

## Phase 1 Exit Criteria

A supported resume can be uploaded and converted into a validated, persisted structured candidate profile.

---

# Phase 2 — Candidate Evidence Model

## Goal

Convert candidate information into atomic, traceable evidence.

---

## M2.1 — Evidence Schema

### Scope

Define:

- evidence types,
- source references,
- provenance,
- metadata.

### Acceptance Criteria

- evidence schema is explicit,
- provenance is preserved,
- evidence records are validated.

---

## M2.2 — Evidence Generation

### Scope

Generate evidence units from:

- experiences,
- projects,
- skills,
- certifications,
- education.

### Acceptance Criteria

- candidate profile data produces atomic evidence records,
- evidence retains source references,
- deterministic generation logic is tested.

---

## M2.3 — Evidence API

### Scope

Support inspection of candidate evidence.

### Acceptance Criteria

- evidence can be retrieved through the API,
- provenance is visible,
- relevant API tests pass.

---

## Phase 2 Exit Criteria

Candidate claims are represented as traceable, inspectable evidence units.

---

# Phase 3 — Job Description Intelligence

## Goal

Convert raw job descriptions into structured requirements.

---

## M3.1 — Job Submission

### Scope

- submit job description text,
- validate content,
- persist source text.

### Acceptance Criteria

- valid job descriptions can be submitted,
- empty or invalid input is rejected,
- source text is preserved.

---

## M3.2 — Requirement Extraction

### Scope

Extract:

- role,
- company,
- seniority,
- skills,
- responsibilities,
- experience,
- education,
- domain requirements.

### Acceptance Criteria

- real job descriptions produce validated structured outputs,
- invalid AI output is controlled,
- extraction behavior is testable.

---

## M3.3 — Requirement Classification

### Scope

Classify requirements as:

- required,
- preferred,
- optional.

### Acceptance Criteria

- extracted requirements have explicit importance classification,
- structured results are persisted.

---

## Phase 3 Exit Criteria

A real job description produces validated, persisted structured requirements.

---

# Phase 4 — Embeddings and Retrieval

## Goal

Retrieve candidate evidence relevant to each job requirement.

---

## M4.1 — pgvector Setup

### Scope

- PostgreSQL integration,
- pgvector extension,
- embedding storage,
- migrations.

### Acceptance Criteria

- pgvector is available,
- vector data can be persisted,
- migrations are reproducible.

---

## M4.2 — Embedding Service

### Scope

- configurable embedding model,
- single-item embedding,
- batch embedding,
- stable service interface.

### Acceptance Criteria

- text can be converted into embeddings,
- embedding dimensions are validated,
- provider and model configuration is explicit.

---

## M4.3 — Evidence Indexing

### Scope

Embed candidate evidence.

### Acceptance Criteria

- candidate evidence can be indexed,
- embeddings remain associated with source evidence.

---

## M4.4 — Semantic Retrieval

### Scope

Retrieve Top-K evidence for job requirements.

### Acceptance Criteria

- requirements retrieve ranked candidate evidence,
- retrieval parameters are configurable,
- relevant tests pass.

---

## M4.5 — Retrieval Evaluation

### Scope

Measure Top-K retrieval quality.

### Acceptance Criteria

- evaluation cases exist,
- retrieval quality can be measured.

---

## Phase 4 Exit Criteria

A job requirement retrieves relevant candidate evidence with measurable retrieval quality.

---

# Phase 5 — Matching and Scoring

## Goal

Produce explainable requirement-level matches and overall scoring.

---

## M5.1 — Match Classification

### Scope

Classify:

- `STRONG_MATCH`,
- `PARTIAL_MATCH`,
- `NO_EVIDENCE`.

### Acceptance Criteria

- requirement matches produce validated classifications,
- evidence references are preserved.

---

## M5.2 — Match Explanation

### Scope

Provide:

- explanation,
- evidence references,
- confidence where appropriate.

### Acceptance Criteria

- users can understand why a requirement received its classification.

---

## M5.3 — Deterministic Scoring

### Scope

Implement weighted scoring components.

Initial conceptual weights:

- required skills: 30%,
- experience alignment: 25%,
- responsibility alignment: 20%,
- preferred skills: 10%,
- education and certifications: 5%,
- semantic evidence quality: 10%.

Weights must be configurable.

### Acceptance Criteria

- final score is calculated deterministically,
- component scores are visible,
- weights are configurable,
- scoring logic has unit tests.

---

## M5.4 — Gap Analysis

### Scope

Identify genuine missing or weak requirements.

### Acceptance Criteria

- requirements with insufficient evidence are surfaced,
- gaps are distinguishable from partial matches.

---

## Phase 5 Exit Criteria

The system produces an explainable score and requirement-level evidence mapping.

---

# Phase 6 — Grounded Resume Tailoring

## Goal

Generate evidence-grounded resume improvements.

---

## M6.1 — Suggestion Schema

### Scope

Represent:

- original text,
- suggested text,
- reason,
- evidence,
- confidence,
- review status.

### Acceptance Criteria

- suggestions use a validated structured schema.

---

## M6.2 — Bullet Rewriting

### Scope

Generate grounded rewrites.

### Acceptance Criteria

- rewrites use supplied candidate evidence,
- original factual meaning is preserved,
- unsupported claims are prohibited.

---

## M6.3 — Grounding Validation

### Scope

Detect unsupported generated claims.

### Acceptance Criteria

- unsupported claims can be identified or rejected,
- grounding evaluation cases exist.

---

## M6.4 — Human Review Workflow

### Scope

Support:

- accept,
- reject,
- edit.

### Acceptance Criteria

- suggestions do not silently overwrite source content,
- review status is persisted.

---

## Phase 6 Exit Criteria

The user can review and approve evidence-grounded resume changes.

---

# Phase 7 — Resume Versioning and Export

## Goal

Create usable job-specific resume artifacts.

---

## M7.1 — Resume Versioning

### Scope

Preserve:

- master version,
- target job,
- accepted changes,
- generated versions.

### Acceptance Criteria

- resume versions are traceable,
- source relationships are preserved.

---

## M7.2 — DOCX Generation

### Scope

Generate professional DOCX output.

### Acceptance Criteria

- accepted content can be exported as a valid DOCX.

---

## M7.3 — PDF Generation

### Scope

Generate PDF output.

### Acceptance Criteria

- accepted content can be exported as a valid PDF.

---

## M7.4 — Application Association

### Scope

Associate a resume version with a job application.

### Acceptance Criteria

- application records can reference the selected resume version.

---

## Phase 7 Exit Criteria

The user can export and preserve a tailored job-specific resume.

---

# Phase 8 — Frontend Product Experience

## Goal

Build the complete interactive user experience.

---

## M8.1 — Application Shell

### Scope

- navigation,
- layout,
- API client,
- frontend configuration.

### Acceptance Criteria

- frontend application runs,
- navigation works,
- backend API communication is configured.

---

## M8.2 — Resume Workflow

### Scope

- resume upload,
- candidate profile review,
- evidence inspection.

### Acceptance Criteria

- the resume workflow is usable through the frontend.

---

## M8.3 — Job Analysis

### Scope

- job description input,
- requirements,
- match score,
- gaps.

### Acceptance Criteria

- job analysis results are visible and understandable.

---

## M8.4 — Tailoring Interface

### Scope

- side-by-side comparison,
- accept,
- reject,
- edit,
- evidence display.

### Acceptance Criteria

- users can review and control AI-generated suggestions.

---

## M8.5 — Application Dashboard

### Scope

- applications,
- resume versions,
- statuses.

### Acceptance Criteria

- users can inspect their application and resume history.

---

## Phase 8 Exit Criteria

The complete core workflow is usable through the frontend.

---

# Phase 9 — Evaluation and Observability

## Goal

Measure and monitor AI behavior.

---

## M9.1 — LLM Run Logging

### Scope

Capture:

- provider,
- model,
- prompt version,
- latency,
- token usage where available,
- status,
- validation result.

### Acceptance Criteria

- relevant LLM executions produce observable metadata.

---

## M9.2 — Evaluation Dataset

### Scope

Create anonymized evaluation examples.

### Acceptance Criteria

- evaluation data exists for core AI workflows,
- private candidate data is not exposed.

---

## M9.3 — Evaluation Runner

### Scope

Evaluate:

- extraction,
- schema compliance,
- matching,
- retrieval,
- groundedness.

### Acceptance Criteria

- evaluations can be executed reproducibly,
- results can be compared.

---

## M9.4 — Internal Metrics

### Scope

Expose useful development metrics.

### Acceptance Criteria

- core AI system behavior can be inspected quantitatively.

---

## Phase 9 Exit Criteria

AI behavior can be measured and compared across system changes.

---

# Phase 10 — Production Hardening

## Goal

Prepare the application for reliable deployment and portfolio presentation.

---

## M10.1 — Security Review

### Scope

Review:

- upload security,
- secrets,
- logging,
- error exposure,
- private data handling.

### Acceptance Criteria

- identified high-priority security issues are resolved or documented.

---

## M10.2 — Continuous Integration

### Scope

Run automatically:

- tests,
- linting,
- type checks.

### Acceptance Criteria

- CI validates repository changes.

---

## M10.3 — Containerization

### Scope

Create production-ready containers.

### Acceptance Criteria

- application components can be built reproducibly.

---

## M10.4 — Deployment

### Scope

Deploy the application.

The exact deployment platform will be selected later.

### Acceptance Criteria

- the application is accessible in the selected deployment environment.

---

## M10.5 — Documentation and Demo

### Scope

Complete:

- README,
- architecture documentation,
- screenshots,
- demo workflow,
- measured portfolio metrics.

### Acceptance Criteria

- the repository clearly explains the problem,
- the architecture is documented,
- setup instructions work,
- the application can be demonstrated,
- measured results are presented accurately.

---

## Phase 10 Exit Criteria

The project is deployable, documented, tested, and portfolio-ready.

---

# Final Project Completion Criteria

The project is considered complete when:

1. a user can upload a resume,
2. the system creates a structured candidate profile,
3. candidate evidence is traceable,
4. a job description can be analyzed,
5. relevant evidence can be retrieved,
6. requirement matches are explainable,
7. the match score is deterministic,
8. genuine gaps are visible,
9. resume suggestions are evidence-grounded,
10. the user can review changes,
11. tailored resumes can be versioned and exported,
12. the core workflow is available through the frontend,
13. AI behavior can be evaluated,
14. the system is tested and documented,
15. the application is deployable.