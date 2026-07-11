# Architecture Decisions

# Purpose

This file records significant architectural decisions.

New major decisions should be added with:

- identifier,
- status,
- context,
- decision,
- rationale,
- consequences where useful.

---

# ADR-001 — Modular Monolith

## Status

Accepted

## Decision

Use a modular monolith for the initial application.

## Rationale

The application does not currently require distributed services.

A modular monolith provides:

- simpler development,
- easier debugging,
- easier deployment,
- clear internal service boundaries,
- lower operational complexity.

---

# ADR-002 — Python 3.14

## Status

Accepted

## Decision

Use Python 3.14 for backend development.

## Constraint

Dependencies must be checked for Python 3.14 compatibility before adoption.

The intended project constraint is:

`>=3.14,<3.15`

---

# ADR-003 — FastAPI

## Status

Accepted

## Decision

Use FastAPI for the backend API.

## Rationale

FastAPI provides:

- Python-native API development,
- Pydantic integration,
- OpenAPI generation,
- dependency injection,
- async support where useful.

---

# ADR-004 — PostgreSQL and pgvector

## Status

Accepted

## Decision

Use PostgreSQL as the primary relational database and pgvector for vector retrieval.

## Rationale

The application domain is relational.

pgvector allows relational data and vector retrieval to coexist without introducing an additional vector database during the initial architecture.

---

# ADR-005 — Provider-Agnostic LLM Layer

## Status

Accepted

## Decision

All LLM interactions must use a provider abstraction.

## Rationale

This prevents business logic from depending directly on a single model provider.

Initial development may use Ollama.

Hosted providers may be added later.

---

# ADR-006 — No Heavy AI Orchestration Framework Initially

## Status

Accepted

## Decision

Do not introduce LangChain or LangGraph as core dependencies in the initial implementation.

## Rationale

The project should expose and teach the underlying GenAI application patterns directly.

Frameworks may be evaluated later if they solve a demonstrated orchestration problem.

---

# ADR-007 — Deterministic Final Match Score

## Status

Accepted

## Decision

The final match score is calculated by deterministic application logic.

LLMs may classify semantic relationships but must not directly invent the final overall score.

## Rationale

This improves:

- explainability,
- reproducibility,
- testability.

---

# ADR-008 — Evidence-Grounded Generation

## Status

Accepted

## Decision

Generated resume claims must be grounded in candidate evidence.

Unsupported claims should be rejected or marked as insufficient evidence.

## Rationale

Resume fabrication is a major product risk.

Grounding is therefore a core system requirement rather than an optional enhancement.

---

# ADR-009 — Human Review Before Applying Suggestions

## Status

Accepted

## Decision

AI-generated resume suggestions must not silently overwrite source content.

Users must be able to:

- accept,
- reject,
- edit.

## Rationale

This preserves user control and reduces the risk of incorrect generated content.

---

# ADR-010 — Incremental Phase-Based Development

## Status

Accepted

## Decision

Develop the application through documented phases and milestones.

## Rationale

The project is intended both as a usable product and as a structured GenAI learning project.

Incremental development improves:

- understanding,
- testability,
- debugging,
- project control.