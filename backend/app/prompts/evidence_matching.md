# Requirement-to-Evidence Matching Prompt (v1)

## Task

Classify how well the candidate's evidence below supports the job requirement below.

## Input Data

Job Requirement:

"""
{requirement_text}
"""

Candidate Evidence (numbered; may be empty):

{evidence_list}

## Output Requirements

Return a single JSON object matching the provided JSON schema exactly.

- `classification`: one of:
  - `STRONG_MATCH` — the evidence directly and clearly demonstrates the requirement.
  - `PARTIAL_MATCH` — the evidence is related but does not fully or directly
    demonstrate the requirement (e.g. an adjacent skill, indirect or older experience,
    partial coverage).
  - `NO_EVIDENCE` — none of the provided evidence meaningfully relates to the
    requirement, or no evidence was provided.
- `explanation`: one to three sentences justifying the classification, referencing
  what the evidence does or does not show.
- `confidence`: a number from 0.0 to 1.0 reflecting how confident you are in this
  classification.
- `supporting_evidence_indices`: the numbers (from the numbered evidence list above)
  of the evidence items that support the classification. Empty list if `NO_EVIDENCE`.

## Grounding Rules

- Base the classification only on the candidate evidence provided above — do not
  assume the candidate has skills, experience, or qualifications not shown in it.
- Do not upgrade a classification because the requirement seems like something a
  candidate in this field "probably" has.
- Only reference evidence indices that were actually provided in the numbered list.
- If no evidence was provided, always return `NO_EVIDENCE` with an empty
  `supporting_evidence_indices` list.

## Prohibited Behavior

- Do not invent candidate qualifications, employers, technologies, or metrics not
  present in the evidence text.
- Do not output anything other than the JSON object.

## Failure Behavior

If the requirement text or evidence is empty, unintelligible, or otherwise
unusable, return `NO_EVIDENCE` with a brief explanation and an empty
`supporting_evidence_indices` list, rather than guessing.
