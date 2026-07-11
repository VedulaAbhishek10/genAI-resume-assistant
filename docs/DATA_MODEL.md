# Data Model

## Purpose

This document describes the conceptual domain model for the GenAI Resume Assistant.

The exact database schema will evolve through implementation and Alembic migrations.

Planned entities must not be treated as implemented until they exist in the codebase and database migrations.

---

# Core Entities

## User

Represents an application user.

Initial local development may use a single-user model.

Future authentication should not require redesigning the entire domain model.

Potential relationships:

- candidate profiles,
- resumes,
- job applications.

---

## CandidateProfile

Represents the normalized master profile of a candidate.

The candidate profile acts as the reusable source of candidate information across multiple job applications.

Contains or relates to:

- professional summary,
- skills,
- experiences,
- projects,
- education,
- certifications.

Conceptually:

```text
CandidateProfile
├── Professional Summary
├── Experiences
├── Projects
├── Skills
├── Education
└── Certifications
```

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

A resume is a document representation.

It is distinct from the complete candidate profile.

---

## ResumeVersion

Represents a specific resume revision.

Potential fields:

- id,
- parent resume ID,
- parent version ID where applicable,
- target job ID,
- accepted suggestions,
- generated document reference,
- creation timestamp.

The system should preserve relationships between:

- master resume,
- generated versions,
- target job.

---

## Experience

Represents professional experience.

Potential information:

- id,
- candidate profile ID,
- employer,
- job title,
- start date,
- end date,
- description,
- achievements.

An experience may produce multiple candidate evidence records.

---

## Project

Represents a candidate project.

Potential information:

- id,
- candidate profile ID,
- name,
- description,
- technologies,
- achievements,
- links.

A project may produce multiple candidate evidence records.

---

## Skill

Represents a normalized candidate skill.

Potential information:

- id,
- candidate profile ID,
- name,
- category.

---

## Education

Represents candidate education.

Potential information:

- institution,
- degree,
- field of study,
- dates,
- achievements.

---

## Certification

Represents a candidate certification.

Potential information:

- name,
- issuing organization,
- issue date,
- credential information where applicable.

---

# Candidate Evidence

## CandidateEvidence

Represents an atomic, retrievable piece of candidate evidence.

Candidate evidence is a core domain concept.

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

Conceptually:

```text
Experience
    │
    ├── Achievement 1 ──► CandidateEvidence
    ├── Achievement 2 ──► CandidateEvidence
    └── Achievement 3 ──► CandidateEvidence

Project
    │
    ├── Project Bullet 1 ──► CandidateEvidence
    └── Project Bullet 2 ──► CandidateEvidence
```

Potential evidence types include:

- experience bullet,
- project bullet,
- achievement,
- skill,
- certification,
- education item.

---

# Job Domain

## JobDescription

Represents submitted job description text.

Potential fields:

- id,
- source text,
- role title,
- company,
- seniority,
- creation timestamp.

The original job description text should be preserved.

---

## JobRequirement

Represents an extracted job requirement.

Potential fields:

- id,
- job description ID,
- text,
- category,
- importance,
- required/preferred status.

Potential categories include:

- skill,
- experience,
- responsibility,
- education,
- certification,
- domain knowledge.

Potential importance classifications include:

- required,
- preferred,
- optional.

---

# Matching Domain

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

A requirement match may reference multiple candidate evidence records.

---

## MatchAnalysis

Represents the complete analysis for a candidate and target job.

Potential information:

- id,
- candidate profile ID,
- job description ID,
- component scores,
- overall score,
- gaps,
- creation timestamp,
- model metadata,
- prompt metadata.

The final overall score must be calculated through deterministic application logic.

---

# Resume Tailoring Domain

## ResumeSuggestion

Represents an AI-generated proposed resume change.

Potential information:

- id,
- match analysis ID,
- source resume content,
- original text,
- suggested text,
- reason,
- evidence references,
- confidence,
- review status.

Possible review statuses:

- `PENDING`
- `ACCEPTED`
- `REJECTED`
- `EDITED`

Suggestions must not silently modify source content.

---

# Application Tracking Domain

## Application

Represents a job application.

Potential information:

- id,
- candidate profile ID,
- company,
- role,
- job description ID,
- selected resume version ID,
- application status,
- creation date,
- application date,
- relevant notes.

Potential application statuses may later include:

- saved,
- preparing,
- applied,
- interview,
- rejected,
- offer,
- withdrawn.

The exact enumeration should be defined during implementation.

---

# AI Observability Domain

## LLMRun

Represents an observable AI operation.

Potential information:

- id,
- operation type,
- provider,
- model,
- prompt version,
- latency,
- input token count where available,
- output token count where available,
- status,
- validation outcome,
- error information where appropriate,
- timestamp.

The application must not store sensitive prompt content unnecessarily.

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
           │
           │ retrieved for
           ▼
      JobRequirement
           │
           ▼
    RequirementMatch
           │
           ▼
      MatchAnalysis
           │
           ▼
    ResumeSuggestion
           │
           ▼
      ResumeVersion


JobDescription
 │
 ├── JobRequirement
 ├── MatchAnalysis
 └── Application
```

---

# Candidate Profile vs Resume

These concepts must remain distinct.

## Candidate Profile

The candidate profile represents the complete known candidate information.

It may contain more information than any individual resume.

## Resume

A resume represents a selected presentation of candidate information.

Different jobs may use different resume versions generated from the same candidate profile.

Conceptually:

```text
Master Candidate Profile
        │
        ├── Data Scientist Resume
        ├── ML Engineer Resume
        └── GenAI Engineer Resume
```

---

# Evidence Provenance

Every candidate evidence record should be traceable to its source.

Conceptually:

```text
CandidateEvidence
    │
    ├── source_entity_type = "experience"
    └── source_entity_id   = "<experience-id>"
```

This provenance is required for:

- explainability,
- grounding,
- human review,
- debugging.

---

# Identifier Policy

Externally exposed identifiers should generally use UUIDs unless a documented architectural decision states otherwise.

---

# Migration Policy

Database schema changes must use Alembic migrations.

Do not manually mutate production database schemas.

---

# Data Privacy

Private candidate information must not be committed to the repository.

Development fixtures should use:

- synthetic data,
- anonymized data,
- intentionally public sample data where legally appropriate.

Do not commit:

- personal resumes,
- private candidate profiles,
- private application information,
- generated private resume files.

---

# Implementation Rule

This document describes the conceptual model.

The implementation should introduce entities incrementally according to the roadmap.

Do not create every planned database table during the initial foundation phase.

Database entities should be implemented when required by the active milestone.