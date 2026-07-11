# API Documentation

# Status

The public application API is not yet implemented.

This document will be updated as API contracts are introduced.

Do not document planned endpoints as implemented endpoints.

---

# API Design Principles

The API should:

- use clear resource-oriented routes,
- use Pydantic request and response schemas,
- return appropriate HTTP status codes,
- return controlled error responses,
- avoid exposing internal implementation details,
- preserve stable contracts where possible.

---

# Planned API Areas

## Health

Potential responsibilities:

- application health,
- readiness where appropriate.

---

## Resumes

Potential responsibilities:

- upload resume,
- retrieve resume,
- retrieve extracted content,
- retrieve structured candidate profile.

---

## Candidate Profiles

Potential responsibilities:

- retrieve candidate profile,
- update reviewed candidate information.

---

## Candidate Evidence

Potential responsibilities:

- list evidence,
- retrieve evidence,
- inspect provenance.

---

## Jobs

Potential responsibilities:

- submit job description,
- retrieve job description,
- retrieve structured requirements.

---

## Matching

Potential responsibilities:

- run match analysis,
- retrieve requirement matches,
- retrieve score breakdown,
- retrieve gaps.

---

## Suggestions

Potential responsibilities:

- generate suggestions,
- retrieve suggestions,
- accept suggestion,
- reject suggestion,
- edit suggestion.

---

## Resume Versions

Potential responsibilities:

- create version,
- retrieve version,
- list versions,
- export DOCX,
- export PDF.

---

## Applications

Potential responsibilities:

- create application,
- retrieve application,
- update application status,
- associate resume version.

---

# Initial Implemented Endpoints

## `GET /health`

Application health check.

Response `200`:

```json
{"status": "ok"}
```

---

## `POST /api/v1/resumes`

Uploads a resume (PDF or DOCX, multipart form field `file`), extracts its text, runs
evidence-grounded structured extraction against the configured LLM provider, and persists
the resulting candidate profile and resume record.

Response `201`:

```json
{
  "id": "uuid",
  "candidate_profile_id": "uuid",
  "filename": "resume.pdf",
  "content_type": "application/pdf",
  "size_bytes": 12345,
  "status": "uploaded",
  "extracted_text": "...",
  "candidate_profile": {
    "professional_summary": "...",
    "experiences": [
      {
        "employer": "...",
        "job_title": "...",
        "start_date": "...",
        "end_date": "...",
        "description": "...",
        "achievements": ["..."]
      }
    ],
    "projects": [{"name": "...", "description": "...", "technologies": ["..."], "achievements": ["..."]}],
    "skills": [{"name": "...", "category": "..."}],
    "education": [{"institution": "...", "degree": "...", "field_of_study": "...", "dates": "...", "achievements": ["..."]}],
    "certifications": [{"name": "...", "issuing_organization": "...", "issue_date": "..."}]
  }
}
```

Controlled error responses use the shape `{"error": {"code": "...", "message": "..."}}`:

| Status | Code                    | Cause                                      |
|--------|-------------------------|---------------------------------------------|
| 415    | `UNSUPPORTED_FILE_TYPE` | File extension is not `.pdf` or `.docx`      |
| 400    | `EMPTY_FILE`             | Uploaded file has no content                 |
| 413    | `FILE_TOO_LARGE`         | File exceeds `MAX_UPLOAD_SIZE_MB`             |
| 400    | `INVALID_DOCUMENT`       | File content does not match its extension    |
| 422    | `EXTRACTION_FAILED`      | Text could not be extracted from the document|
| 422    | `LLM_OUTPUT_INVALID`     | LLM structured output failed schema validation after retries |
| 502    | `LLM_PROVIDER_ERROR`     | The configured LLM provider was unreachable or errored |

---

## `GET /api/v1/candidate-profiles/{candidate_profile_id}/evidence`

Lists atomic, traceable `CandidateEvidence` units generated deterministically (no LLM
call) from a persisted candidate profile's experiences, projects, skills, education, and
certifications.

Response `200`:

```json
[
  {
    "id": "uuid",
    "candidate_profile_id": "uuid",
    "evidence_type": "experience_bullet | project_bullet | achievement | skill | certification | education_item",
    "source_entity_type": "experience | project | skill | education | certification",
    "source_entity_id": "uuid",
    "text": "...",
    "evidence_metadata": {"...": "..."},
    "created_at": "2026-01-01T00:00:00"
  }
]
```

`404 NOT_FOUND` if `candidate_profile_id` does not exist.

---

## `POST /api/v1/jobs`

Submits job description text, extracts structured requirements via the configured LLM
provider, and persists both.

Request:

```json
{"text": "Senior Backend Engineer at Example Corp. Requirements: 5+ years of Python..."}
```

`text` must be non-blank (`422 VALIDATION_ERROR` otherwise).

Response `201`:

```json
{
  "id": "uuid",
  "source_text": "...",
  "role_title": "Senior Backend Engineer",
  "company": "Example Corp",
  "seniority": "senior",
  "requirements": [
    {
      "id": "uuid",
      "text": "5+ years of Python experience",
      "category": "skill | experience | responsibility | education | certification | domain_knowledge",
      "importance": "required | preferred | optional"
    }
  ],
  "created_at": "2026-01-01T00:00:00"
}
```

Uses the same `LLM_OUTPUT_INVALID` (422) / `LLM_PROVIDER_ERROR` (502) controlled errors
as resume extraction (see above) if the LLM provider fails.

---

## `GET /api/v1/candidate-profiles/{candidate_profile_id}/retrieve`

Retrieves the top-K candidate evidence units semantically closest to a free-text query
(typically a job requirement's `text`), ranked by cosine similarity over embeddings
computed with the configured embedding model (`EMBEDDING_MODEL`).

Query parameters:

- `query` (required, non-blank): the text to find relevant evidence for.
- `top_k` (optional, 1–50): overrides the configured `RETRIEVAL_TOP_K` default.

Response `200`:

```json
[
  {
    "evidence": { "...": "... (same shape as GET .../evidence items)" },
    "similarity": 0.83
  }
]
```

Results are ordered by descending `similarity` (`1 - cosine_distance`). `404 NOT_FOUND`
if `candidate_profile_id` does not exist; `422` if `query` is blank/missing.

---

## `POST /api/v1/match-analyses`

Runs a full match analysis for a candidate profile against a job description: for
each of the job's requirements, retrieves relevant candidate evidence, classifies the
match via the LLM (`STRONG_MATCH`/`PARTIAL_MATCH`/`NO_EVIDENCE`), then computes the
final score **deterministically** from those classifications (the LLM never sets the
overall score directly — see ADR-007).

Request:

```json
{"candidate_profile_id": "uuid", "job_description_id": "uuid"}
```

Response `201`:

```json
{
  "id": "uuid",
  "candidate_profile_id": "uuid",
  "job_description_id": "uuid",
  "overall_score": 0.46,
  "component_scores": {
    "required_skills": 1.0,
    "experience_alignment": 0.25,
    "semantic_evidence_quality": 0.99
  },
  "requirement_matches": [
    {
      "id": "uuid",
      "job_requirement_id": "uuid",
      "requirement_text": "Experience with Python",
      "category": "experience",
      "importance": "required",
      "classification": "STRONG_MATCH",
      "explanation": "...",
      "confidence": 1.0,
      "evidence": [{ "...": "... (CandidateEvidenceRead)" }]
    }
  ],
  "gaps": [
    {
      "requirement_text": "Experience with Kubernetes",
      "category": "experience",
      "importance": "required",
      "classification": "NO_EVIDENCE"
    }
  ],
  "created_at": "2026-01-01T00:00:00"
}
```

`component_scores` only includes components with at least one requirement in that
bucket (see `docs/ROADMAP.md` M5.3); remaining weights are renormalized so an
analysis is never penalized for a job posting that, say, has no certification
requirements. `gaps` includes every `NO_EVIDENCE` requirement plus any `required`
requirement that only scored `PARTIAL_MATCH`.

`404 NOT_FOUND` if either ID does not exist. Uses the same `LLM_OUTPUT_INVALID` (422)
/ `LLM_PROVIDER_ERROR` (502) controlled errors as other LLM-backed endpoints.

This section must be updated as further endpoints are implemented.