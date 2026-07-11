# Requirements

# Functional Requirements

## FR-001 — Resume Upload

The user must be able to upload:

- PDF,
- DOCX.

The system must validate:

- supported file type,
- file size,
- empty files,
- invalid or unreadable documents.

---

## FR-002 — Resume Text Extraction

The system must extract text from supported documents.

The original document and extracted representation must remain distinguishable.

---

## FR-003 — Structured Candidate Profile

The system must extract and represent:

- professional summary,
- work experience,
- projects,
- skills,
- education,
- certifications,
- achievements where available.

Structured AI outputs must be schema validated.

---

## FR-004 — Candidate Evidence Units

The system must create retrievable evidence units from candidate data.

Evidence types may include:

- experience bullet,
- project bullet,
- achievement,
- skill,
- certification,
- education item.

Each evidence unit must preserve provenance.

---

## FR-005 — Job Description Input

The user must be able to submit job description text.

The system must validate empty or invalid input.

---

## FR-006 — Job Requirement Extraction

The system must extract:

- role title,
- company if available,
- seniority,
- required skills,
- preferred skills,
- responsibilities,
- experience requirements,
- education requirements,
- domain knowledge.

Requirements should be classified by importance.

---

## FR-007 — Semantic Evidence Retrieval

For a job requirement, the system must retrieve relevant candidate evidence using semantic similarity.

---

## FR-008 — Requirement Matching

The system must classify candidate alignment as:

- `STRONG_MATCH`
- `PARTIAL_MATCH`
- `NO_EVIDENCE`

The result should include:

- explanation,
- supporting evidence references.

---

## FR-009 — Match Scoring

The system must calculate an overall match score using deterministic weighted components.

The score must be:

- decomposable,
- explainable,
- reproducible for the same classified inputs.

---

## FR-010 — Gap Analysis

The system must identify requirements for which candidate evidence is missing or weak.

---

## FR-011 — Resume Suggestions

The system must generate evidence-grounded suggestions.

Suggestions may include:

- rewriting,
- prioritization,
- reordering,
- terminology alignment.

---

## FR-012 — Suggestion Review

The user must be able to:

- accept,
- reject,
- edit.

---

## FR-013 — Resume Versioning

The system must preserve:

- master resume,
- generated versions,
- target job association,
- creation timestamp,
- revision relationships where applicable.

---

## FR-014 — Export

The system should support:

- DOCX export,
- PDF export.

---

## FR-015 — Application Tracking

The system should associate:

- company,
- role,
- job description,
- analysis,
- selected resume version,
- application status.

---

# Non-Functional Requirements

## NFR-001 — Maintainability

The system must use modular, documented architecture.

---

## NFR-002 — Type Safety

Backend code should use Python type hints.

Frontend code should use TypeScript.

---

## NFR-003 — Testability

Core deterministic logic must be unit testable without requiring a live LLM.

---

## NFR-004 — Privacy

Private resume and candidate data must not be committed to Git.

---

## NFR-005 — Observability

LLM operations should eventually capture:

- model,
- provider,
- prompt version,
- latency,
- token usage where available,
- execution status,
- validation result.

---

## NFR-006 — Explainability

Scores and suggestions should expose the relevant inputs used to produce them.

---

## NFR-007 — Groundedness

Generated candidate claims must be supported by available candidate evidence.

---

## NFR-008 — Reliability

External AI failures must produce controlled application errors.

---

## NFR-009 — Reproducibility

Dependencies and runtime requirements must be explicitly defined.

---

## NFR-010 — Security

Uploads and user-controlled content must be treated as untrusted input.

---

## NFR-011 — Configurability

The following should be configurable where appropriate:

- LLM provider,
- model name,
- embedding model,
- scoring weights,
- environment-specific settings.

---

## NFR-012 — Incremental Development

The application must be developed through documented milestones with explicit acceptance criteria.