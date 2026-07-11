
---

# `docs/DATA_MODEL.md`

```markdown
# Data Model

# Purpose

This document describes the conceptual domain model.

The exact database schema will evolve through implementation and Alembic migrations.

Planned entities must not be treated as implemented until they exist in the codebase and database migrations.

---

# Core Entities

## User

Represents an application user.

Initial local development may use a single-user model.

Future authentication should not require redesigning the entire domain model.

---

## CandidateProfile

Represents the normalized master profile of a candidate.

Contains or relates to:

- professional summary,
- skills,
- experiences,
- projects,
- education,
- certifications.

---

## Resume

Represents an uploaded or generated resume document.

Potential fields:

- id,
- candidate profile ID,
- name,
- document type,
- source file reference,
- extracted text,
- creation timestamp.

---

## ResumeVersion

Represents a specific resume revision.

Potential fields:

- id,
- parent resume or version,
- target job,
- accepted suggestions,
- generated document reference,
- creation timestamp.

---

## Experience

Represents professional experience.

Potential information:

- employer,
- title,
- start date,
- end date,
- description,
- achievements.

---

## Project

Represents a candidate project.

Potential information:

- name,
- description,
- technologies,
- achievements,
- links.

---

## Skill

Represents a normalized candidate skill.

---

## Education

Represents candidate education.

---

## Certification

Represents a candidate certification.

---

## CandidateEvidence

Represents an atomic retrievable piece of candidate evidence.

Potential fields:

- id,
- candidate profile ID,
- evidence type,
- source entity type,
- source entity ID,
- text,
- metadata,
- embedding,
- creation timestamp.

The evidence record must preserve provenance.

---

## JobDescription

Represents submitted job description text.

Potential fields:

- id,
- source text,
- role title,
- company,
- creation timestamp.

---

## JobRequirement

Represents an extracted requirement.

Potential fields:

- id,
- job description ID,
- text,
- category,
- importance,
- required/preferred status.

---

## RequirementMatch

Represents the relationship between a job requirement and candidate evidence.

Potential fields:

- id,
- requirement ID,
- classification,
- explanation,
- confidence,
- evidence references.

Possible classifications:

- `STRONG_MATCH`
- `PARTIAL_MATCH`
- `NO_EVIDENCE`

---

## MatchAnalysis

Represents the complete analysis for a candidate and job.

Potential information:

- component scores,
- overall score,
- gaps,
- creation timestamp,
- model metadata,
- prompt metadata.

---

## ResumeSuggestion

Represents an AI-generated proposed change.

Potential information:

- original text,
- suggested text,
- reason,
- evidence references,
- confidence,
- review status.

Possible statuses:

- `PENDING`
- `ACCEPTED`
- `REJECTED`
- `EDITED`

---

## Application

Represents a job application.

Potential information:

- company,
- role,
- job description,
- selected resume version,
- application status,
- relevant dates.

---

## LLMRun

Represents an observable AI operation.

Potential information:

- operation type,
- provider,
- model,
- prompt version,
- latency,
- token counts,
- status,
- validation outcome,
- timestamp.

---

# Conceptual Relationship Summary

```text
User
  │
  ▼
CandidateProfile
  │
  ├── Resume
  │     │
  │     ▼
  │   ResumeVersion
  │
  ├── Experience
  ├── Project
  ├── Skill
  ├── Education
  ├── Certification
  │
  └── CandidateEvidence


JobDescription
  │
  ├── JobRequirement
  │      │
  │      ▼
  │   RequirementMatch
  │
  ├── MatchAnalysis
  ├── ResumeSuggestion
  │
  └── Application