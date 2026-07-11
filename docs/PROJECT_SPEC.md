# Project Specification

## Project Name

GenAI Resume Assistant

---

# Product Summary

The GenAI Resume Assistant is an evidence-grounded application that helps users analyze job descriptions and tailor resumes using verified information from a reusable candidate profile.

The application combines:

- document parsing,
- structured LLM extraction,
- candidate evidence modeling,
- embeddings,
- semantic retrieval,
- requirement matching,
- deterministic scoring,
- grounded generation,
- human review,
- resume versioning,
- application tracking.

---

# Problem Statement

Job seekers frequently need to tailor their resumes for different job descriptions.

The common workflow is inefficient:

1. read a job description,
2. identify important requirements,
3. compare those requirements with existing experience,
4. determine which experiences and projects are most relevant,
5. rewrite resume bullets,
6. align terminology with the target role,
7. ensure important qualifications are represented,
8. avoid overstating or fabricating experience,
9. generate and manage multiple resume versions.

Generic LLM-based resume tools often have several weaknesses:

- they treat the resume as an unstructured text blob,
- they produce arbitrary or unexplained match scores,
- they may fabricate candidate experience,
- they provide little evidence for recommendations,
- they do not maintain a reusable candidate knowledge base,
- they provide limited human review,
- they rarely evaluate generated claims for groundedness.

This project addresses those limitations.

---

# Product Goal

Build a system that transforms:

1. a structured candidate evidence base, and
2. a target job description

into:

- structured job requirements,
- requirement-level candidate evidence matches,
- genuine skill and experience gaps,
- an explainable match score,
- evidence-grounded resume suggestions,
- a human-approved tailored resume.

---

# Core Product Principle

The AI may:

- rewrite,
- clarify,
- reorder,
- prioritize,
- summarize,
- align terminology.

The AI must not:

- invent experience,
- invent skills,
- invent metrics,
- invent technologies,
- invent employers,
- invent responsibilities,
- invent education,
- invent certifications,
- invent projects.

When candidate evidence is insufficient, the application should expose the gap rather than fabricate a qualification.

---

# Initial Target User

The initial target user is an active technical job seeker applying to roles such as:

- Data Scientist,
- Machine Learning Engineer,
- AI Engineer,
- GenAI Engineer,
- Data Analyst,
- related technical roles.

The architecture should remain sufficiently general to support other professional domains later.

---

# Primary User Journey

## Step 1 — Build Candidate Profile

The user uploads a master resume.

The system:

- validates the document,
- extracts text,
- identifies resume sections,
- creates structured candidate data,
- allows future review and correction,
- converts candidate information into retrievable evidence units.

---

## Step 2 — Add Target Job

The user submits a job description.

The system extracts:

- role title,
- company if available,
- seniority,
- required skills,
- preferred skills,
- responsibilities,
- experience requirements,
- education requirements,
- domain requirements.

---

## Step 3 — Retrieve Candidate Evidence

For each job requirement, the system:

- searches the candidate evidence base,
- retrieves the most relevant evidence,
- preserves evidence provenance.

Example:

```text
Job Requirement:
"Experience building automated ML evaluation pipelines"

Retrieved Candidate Evidence:
1. Automated validation framework experience
2. Audio quality metric evaluation pipeline
3. ML model evaluation project experience
```

---

## Step 4 — Match Requirements

For each job requirement, the system classifies the candidate relationship as:

- `STRONG_MATCH`
- `PARTIAL_MATCH`
- `NO_EVIDENCE`

The system provides:

- classification,
- explanation,
- supporting evidence.

A `NO_EVIDENCE` result must not trigger fabricated candidate information.

---

## Step 5 — Calculate Match Score

The application calculates a deterministic weighted score from defined scoring components.

The LLM may contribute semantic classifications.

The LLM must not directly invent the final overall score.

The score should be decomposable into understandable components.

---

## Step 6 — Generate Suggestions

The application proposes:

- bullet rewrites,
- content prioritization,
- terminology alignment,
- section-level improvements.

Generated claims must be grounded in candidate evidence.

---

## Step 7 — Human Review

The user can:

- accept,
- reject,
- edit.

AI-generated suggestions do not silently overwrite the source resume.

---

## Step 8 — Generate Tailored Resume

The application creates a job-specific resume version using approved changes.

---

## Step 9 — Export and Track

The user can:

- export the resume,
- preserve the generated version,
- associate it with a job application.

---

# Core Product Workflow

```text
Master Resume
     │
     ▼
Document Parsing
     │
     ▼
Structured Candidate Profile
     │
     ▼
Candidate Evidence Store
     │
     │
     │             Target Job Description
     │                     │
     │                     ▼
     │            Requirement Extraction
     │                     │
     └──────────┬──────────┘
                │
                ▼
        Evidence Retrieval
                │
                ▼
       Requirement Matching
                │
                ▼
        Deterministic Score
                │
                ▼
           Gap Analysis
                │
                ▼
       Grounded Suggestions
                │
                ▼
          Human Review
                │
                ▼
        Tailored Resume
                │
                ▼
          DOCX / PDF
```

---

# Initial Success Criteria

The project is successful when a user can:

1. upload a supported resume,
2. obtain a validated structured candidate profile,
3. inspect reusable candidate evidence,
4. submit a real job description,
5. obtain structured job requirements,
6. see relevant candidate evidence for each requirement,
7. understand genuine gaps,
8. receive an explainable match score,
9. review grounded resume suggestions,
10. generate a tailored resume,
11. export and preserve the resume version.

---

# Product Differentiators

## Evidence Grounding

Generated candidate claims are connected to source evidence.

---

## Explainable Matching

Requirement matches expose supporting candidate evidence.

---

## Deterministic Scoring

The final match score is calculated by application logic rather than invented directly by an LLM.

---

## Human Review

The user controls whether generated changes are accepted.

---

## Reusable Candidate Profile

The candidate's complete evidence base can be reused across multiple job applications.

A resume is treated as one presentation of the candidate profile rather than the entire source of truth.

---

## Evaluation

AI behavior is measured rather than judged only through subjective impressions.

---

# Initial Product Scope

The initial complete product should support:

- PDF resume upload,
- DOCX resume upload,
- structured resume extraction,
- candidate profile creation,
- candidate evidence generation,
- job description submission,
- job requirement extraction,
- semantic evidence retrieval,
- requirement matching,
- deterministic match scoring,
- gap analysis,
- evidence-grounded resume suggestions,
- human review,
- resume versioning,
- DOCX export,
- PDF export,
- basic application tracking.

---

# Non-Goals for Initial Versions

The initial project will not focus on:

- automatic job application submission,
- browser automation,
- scraping protected job platforms,
- autonomous job-application agents,
- social network automation,
- interview coaching,
- cover letter generation,
- custom LLM fine-tuning,
- multi-agent orchestration,
- knowledge graphs.

These may be evaluated later only if they provide clear product value.

---

# Technical Learning Objectives

The project should provide practical experience with:

- LLM integration,
- prompt engineering,
- structured outputs,
- Pydantic validation,
- embeddings,
- vector search,
- semantic retrieval,
- evidence grounding,
- hallucination prevention,
- deterministic scoring,
- human-in-the-loop systems,
- document processing,
- LLM evaluation,
- prompt versioning,
- AI observability,
- production API design.

---

# Product Quality Principle

The goal is not to build the largest possible GenAI system.

The goal is to build a clear, useful, testable, evidence-grounded GenAI application whose architecture can be explained and defended technically.