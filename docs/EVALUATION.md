# AI Evaluation Strategy

## Purpose

This document defines how AI behavior in the GenAI Resume Assistant is measured, so
that quality is assessed objectively rather than through subjective impression alone.

See `docs/AI_SYSTEM.md`'s "AI Evaluation" section for the high-level responsibilities
this document expands on.

---

# Principles

- Evaluation must use synthetic or anonymized data only. Private candidate or job
  application data must never be used as evaluation fixtures (see `docs/DATA_MODEL.md`,
  "Data Privacy").
- Evaluation must be reproducible: the same inputs, prompt version, and model
  configuration should produce comparable results.
- Evaluation runs are distinct from correctness tests. `make test` verifies
  deterministic application logic and controlled error handling; evaluation runs
  measure the *quality* of AI outputs and may require a live LLM or embedding model.
  Evaluation runs are not part of the default `make test` suite.

---

# Evaluation Dimensions

## 1. Structured Extraction Quality

Applies to resume extraction (`app/services/resume_parser.py`) and job description
extraction (`app/services/jd_analyzer.py`).

- **Schema compliance rate**: proportion of runs producing valid structured output
  without exhausting retries.
- **Field-level accuracy**: agreement between extracted fields and hand-labeled
  expected values for a small labeled example set.

## 2. Retrieval Quality

Applies to semantic evidence retrieval (`app/services/retrieval_service.py`,
introduced in Phase 4).

- For a labeled set of `(job_requirement_text, expected_relevant_evidence_text)`
  pairs, measure whether the expected evidence appears in the top-K retrieved
  results (recall@K).

## 3. Requirement Matching Quality

Applies to requirement-to-evidence classification (Phase 5,
`STRONG_MATCH`/`PARTIAL_MATCH`/`NO_EVIDENCE`).

- Classification agreement against a hand-labeled expected classification for each
  labeled `(requirement, evidence)` pair.

## 4. Groundedness

Applies to generated resume suggestions (Phase 6).

- Whether a generated suggestion's claims are traceable to the evidence it was given;
  unsupported claims should be flagged or rejected (see ADR-008).

## 5. Stability

- Variance in structured output across repeated runs of the same input at low
  temperature. High variance in a supposedly deterministic-leaning task indicates a
  prompt or configuration issue.

---

# Evaluation Data

- Synthetic resumes, job descriptions, and expected outputs only — no real personal
  data.
- Small, clearly synthetic examples used purely for correctness tests live under
  `backend/tests/fixtures/` (version-controlled).
- Larger or evolving evaluation datasets live under `data/evaluation/` (gitignored per
  `docs/DATA_MODEL.md`'s Data Privacy section; not committed).

---

# Evaluation Runner

- Introduced incrementally: retrieval evaluation starts in Phase 4 (M4.5); extraction,
  matching, and groundedness evaluation are expanded in Phase 9 (M9.2–M9.4).
- Each evaluation run should report, at minimum:
  - the metric name and score,
  - the number of examples evaluated,
  - the prompt version and model used (see `docs/AI_SYSTEM.md`, "Prompt Versioning").
- Evaluation runners must be executable independently of the API (plain scripts or
  pytest-marked tests), so they can be re-run after a prompt or model change to
  compare results.

---

# Relationship to LLM Observability

Evaluation measures aggregate quality across an example set. LLM run observability
(`docs/DATA_MODEL.md`'s `LLMRun` entity, Phase 9 M9.1) captures per-request operational
data (latency, provider, status, validation outcome). The two are complementary:
observability answers "what happened on this request," evaluation answers "how good is
the system, overall, right now."
