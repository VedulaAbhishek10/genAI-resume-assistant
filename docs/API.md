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

None yet.

This section must be updated when endpoints are actually implemented.