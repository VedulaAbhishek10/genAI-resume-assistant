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

This section must be updated as further endpoints are implemented.