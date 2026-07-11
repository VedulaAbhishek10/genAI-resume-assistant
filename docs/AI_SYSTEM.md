# AI System Design

## Purpose

This document defines the role of AI components in the GenAI Resume Assistant.

The system uses Large Language Models and embeddings only where semantic understanding provides meaningful value.

Deterministic application logic remains responsible for deterministic tasks.

The AI system must be designed around four principles:

1. structured outputs,
2. evidence grounding,
3. traceability,
4. controlled failure handling.

---

# AI Responsibilities

The AI system is responsible for semantic tasks including:

- resume structure extraction,
- candidate information extraction,
- job requirement extraction,
- semantic requirement interpretation,
- requirement-to-evidence classification,
- grounded resume rewriting,
- natural-language explanations.

---

# AI Non-Responsibilities

The AI system should not be responsible for:

- final arithmetic score calculation,
- database identifiers,
- file validation,
- schema enforcement,
- authorization,
- persistence logic,
- deterministic sorting,
- deterministic filtering,
- timestamps,
- application state management.

These tasks must be handled through deterministic application logic.

---

# Core AI Pipeline

The overall AI workflow is:

```text
Resume
   │
   ▼
Structured Candidate Extraction
   │
   ▼
Candidate Profile
   │
   ▼
Candidate Evidence Units
   │
   ▼
Embeddings and Vector Index
   │
   │
   │                 Job Description
   │                        │
   │                        ▼
   │              Requirement Extraction
   │                        │
   │                        ▼
   │                 Job Requirements
   │                        │
   └───────────────┬────────┘
                   │
                   ▼
           Evidence Retrieval
                   │
                   ▼
          Requirement Matching
                   │
                   ▼
        Deterministic Scoring
                   │
                   ▼
             Gap Analysis
                   │
                   ▼
       Grounded Resume Tailoring
                   │
                   ▼
             Human Review
```

---

# LLM Abstraction

All LLM operations must pass through a provider abstraction.

Direct model calls must not be scattered throughout application services or API routes.

The conceptual interface is:

```python
class LLMClient:
    async def generate(self, ...):
        ...

    async def generate_structured(self, ...):
        ...
```

The exact interface should be implemented when required by the active development milestone.

Provider-specific implementations must remain isolated.

Potential providers include:

- Ollama for local model execution,
- hosted LLM providers added later.

The rest of the application should depend on the abstraction rather than a specific provider.

---

# Structured Output Pipeline

Whenever downstream application logic depends on an LLM response, structured output should be preferred.

The expected pipeline is:

```text
Prompt
+
Input Data
+
Expected Output Schema
        │
        ▼
       LLM
        │
        ▼
   Raw Response
        │
        ▼
      Parsing
        │
        ▼
Pydantic Validation
        │
        ▼
Validated Application Data
```

Invalid model output must not silently enter application state.

The system must explicitly handle:

- malformed responses,
- missing required fields,
- invalid enum values,
- schema validation failures,
- empty responses.

---

# Candidate Evidence

Candidate evidence is the source of truth for generated candidate claims.

A candidate evidence record represents an atomic, traceable piece of information about the candidate.

Conceptual example:

```json
{
  "id": "uuid",
  "type": "experience_bullet",
  "source_id": "uuid",
  "text": "Developed automated validation tools for speech enhancement evaluation.",
  "metadata": {
    "company": "Example Company"
  }
}
```

Each evidence record must preserve provenance.

---

# Evidence Types

Potential evidence types include:

- experience bullet,
- project bullet,
- achievement,
- skill,
- certification,
- education item.

The exact enumeration will be implemented during the Candidate Evidence phase.

---

# Embedding System

Candidate evidence units will be converted into vector embeddings.

The embedding system should provide:

- configurable embedding model,
- single-text embedding,
- batch embedding,
- explicit embedding dimensions,
- stable service interface.

The initial embedding implementation will use a local sentence-transformers model.

The exact model must remain configurable.

---

# Retrieval Pipeline

The retrieval pipeline is:

```text
Job Requirement
        │
        ▼
Requirement Embedding
        │
        ▼
pgvector Similarity Search
        │
        ▼
Top-K Candidate Evidence
        │
        ▼
Optional Metadata Filtering
        │
        ▼
Matching Context
```

The system should preserve:

- evidence IDs,
- similarity scores where useful,
- evidence provenance.

Retrieval quality should eventually be evaluated using labeled examples.

---

# Matching Pipeline

The matching system receives:

- one job requirement,
- retrieved candidate evidence.

It produces one of the following classifications:

- `STRONG_MATCH`
- `PARTIAL_MATCH`
- `NO_EVIDENCE`

The output should include:

- classification,
- explanation,
- evidence IDs,
- confidence where useful.

The LLM may perform semantic classification.

The classification result must be validated before downstream use.

---

# Match Scoring

The final overall resume-to-job match score must not be directly invented by an LLM.

The expected flow is:

```text
Job Requirements
        │
        ▼
Requirement-Level Matches
        │
        ▼
Validated Match Classifications
        │
        ▼
Deterministic Weighted Scoring
        │
        ▼
Component Scores
        │
        ▼
Overall Match Score
```

LLMs may contribute semantic classifications.

Application code calculates the final score.

---

# Grounded Resume Generation

Resume suggestions must use supplied candidate evidence.

The model must be instructed to:

- preserve factual meaning,
- avoid unsupported technologies,
- avoid invented metrics,
- avoid inflated achievements,
- avoid invented responsibilities,
- avoid invented years of experience,
- avoid invented employers,
- return insufficient evidence when necessary.

The AI may:

- improve wording,
- improve clarity,
- prioritize relevant information,
- align terminology,
- restructure existing information.

The AI must not create unsupported candidate claims.

---

# Conceptual Suggestion Output

A resume suggestion may use a structure such as:

```json
{
  "original_text": "Developed Python tools for audio validation.",
  "suggested_text": "Developed automated Python-based validation tools for evaluating speech enhancement quality.",
  "reason": "Improves alignment with the target role's requirement for automated ML evaluation.",
  "evidence_ids": [
    "evidence-uuid"
  ],
  "confidence": 0.92
}
```

The exact schema will be implemented during the relevant milestone.

---

# Human-in-the-Loop Workflow

AI-generated suggestions must not silently overwrite resume content.

The workflow is:

```text
Original Content
        │
        ▼
AI Suggestion
        │
        ├── Suggested Text
        ├── Explanation
        ├── Evidence
        └── Confidence
        │
        ▼
    Human Review
        │
        ├── Accept
        ├── Reject
        └── Edit
```

Only approved content should become part of a generated resume version.

---

# Prompt Storage

Production prompts are stored under:

```text
backend/app/prompts/
```

Initial planned prompts:

- `resume_extraction.md`
- `jd_extraction.md`
- `evidence_matching.md`
- `bullet_rewriting.md`

---

# Prompt Design Requirements

Each production prompt should define:

- task,
- input data,
- available evidence,
- output requirements,
- grounding rules,
- prohibited behavior,
- failure behavior.

Prompts should not rely on vague instructions where explicit constraints are possible.

---

# Prompt Versioning

Prompts that materially affect AI behavior should have identifiable versions.

Prompt version information should eventually be recorded with LLM execution metadata.

A material prompt change should be evaluated against the existing evaluation dataset.

---

# Model Configuration

The initial development provider is Ollama.

The exact model name must be configurable through environment variables.

No service should assume a hardcoded model name.

Hosted providers may be added later behind the same abstraction.

---

# Temperature Guidance

Use lower temperatures for:

- extraction,
- classification,
- schema-constrained generation.

Use moderate temperature only where controlled rewriting benefits from variation.

Temperature should be configurable by task where necessary.

---

# Failure Handling

The AI layer must eventually handle:

- provider unavailable,
- request timeout,
- empty response,
- malformed structured output,
- schema validation failure,
- unsupported provider configuration.

Retries must be bounded.

Do not create infinite retry loops.

AI failures should produce controlled application errors.

---

# Grounding Principle

A fluent response is not necessarily a valid response.

The system should prioritize:

1. evidence,
2. correctness,
3. traceability,
4. clarity,
5. style.

Style must never override factual grounding.

---

# AI Evaluation

AI behavior should eventually be evaluated for:

- structured extraction quality,
- schema compliance,
- retrieval quality,
- requirement matching quality,
- groundedness,
- stability.

The detailed evaluation strategy is defined in:

`docs/EVALUATION.md`