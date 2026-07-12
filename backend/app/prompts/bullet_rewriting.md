# Grounded Bullet Rewriting Prompt (v1)

## Task

Rewrite the candidate's existing resume bullet below so it aligns better with the
target job requirement, using only facts already present in the original text.

## Input Data

Target Job Requirement:

"""
{requirement_text}
"""

Original Resume Bullet:

"""
{original_text}
"""

## Output Requirements

Return a single JSON object matching the provided JSON schema exactly.

- `suggested_text`: the rewritten bullet.
- `reason`: one sentence explaining how the rewrite better aligns with the
  requirement (e.g. terminology alignment, clarity, prioritization).
- `confidence`: a number from 0.0 to 1.0 reflecting how confident you are that the
  rewrite is fully supported by the original text.

## Grounding Rules

- You may: reword, clarify, reorder, prioritize, and align terminology with the
  requirement's language (e.g. "built REST APIs" → "developed RESTful APIs" if the
  requirement uses that phrasing and the original supports it).
- You must not add any employer, job title, technology, skill, responsibility,
  metric, number, date, or achievement that is not already stated in the original
  text.
- If the original text does not support a meaningfully better alignment with the
  requirement, return `suggested_text` equal to the original text and explain why
  in `reason`, rather than inventing improvements.

## Prohibited Behavior

- Do not invent or estimate metrics (percentages, counts, durations) not present in
  the original text.
- Do not imply broader scope, seniority, or impact than the original text supports.
- Do not output anything other than the JSON object.

## Failure Behavior

If the original text is empty or unusable, return it unchanged as `suggested_text`
with a `reason` noting there was nothing to improve, and a low `confidence`.
