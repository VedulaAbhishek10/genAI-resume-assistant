# Resume Structured Extraction Prompt (v1)

## Task

Extract a structured candidate profile from the resume text below. Represent only
information that is explicitly present in the resume text.

## Input Data

Resume text:

"""
{resume_text}
"""

## Output Requirements

Return a single JSON object matching the provided JSON schema exactly. Do not include
any text, explanation, or markdown outside the JSON object.

- `professional_summary`: a short summary if the resume states one, otherwise null.
- `experiences`: one entry per distinct job/role, in the order they appear.
- `projects`: one entry per distinct project.
- `skills`: one entry per distinct skill mentioned.
- `education`: one entry per distinct degree or program.
- `certifications`: one entry per distinct certification.

## Grounding Rules

- Only extract information that is explicitly stated in the resume text.
- Do not invent employers, job titles, dates, metrics, technologies, skills,
  responsibilities, degrees, or certifications that are not present in the text.
- If a field is not present for an item, use `null` (or an empty list, where
  applicable) rather than guessing a plausible value.
- If the resume text contains no information for an entire section (for example, no
  certifications), return an empty list for that section rather than fabricating
  entries.

## Prohibited Behavior

- Do not add years of experience, seniority claims, or achievements not stated in
  the text.
- Do not normalize or infer employment dates that are not written in the text.
- Do not output anything other than the JSON object.

## Failure Behavior

If the resume text is empty, unintelligible, or contains no identifiable resume
content, return a JSON object with all fields `null` or empty rather than fabricating
a plausible-looking profile.
