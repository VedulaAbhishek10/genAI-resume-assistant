# Job Requirement Extraction Prompt (v1)

## Task

Extract structured job requirements from the job description text below. Represent
only information that is explicitly present in the text.

## Input Data

Job description text:

"""
{job_text}
"""

## Output Requirements

Return a single JSON object matching the provided JSON schema exactly. Do not include
any text, explanation, or markdown outside the JSON object.

- `role_title`: the job title, if stated, otherwise `null`.
- `company`: the hiring company name, if stated, otherwise `null`.
- `seniority`: a seniority level (e.g. "junior", "mid", "senior", "staff"), only if it
  is explicitly stated or unambiguously implied by the title (e.g. "Senior Engineer");
  otherwise `null`.
- `requirements`: one entry per distinct requirement, each with:
  - `text`: the requirement as stated (may be lightly cleaned up for clarity).
  - `category`: one of `skill`, `experience`, `responsibility`, `education`,
    `certification`, `domain_knowledge`.
  - `importance`: `required` if the text presents it as mandatory (e.g. "must have",
    "required", listed under a "Requirements" heading), `preferred` if presented as a
    plus/nice-to-have (e.g. "preferred", "nice to have", "bonus", listed under a
    "Preferred Qualifications" heading), or `optional` if importance is unclear or the
    text merely mentions the item without emphasis.

## Grounding Rules

- Only extract requirements explicitly stated or clearly implied by the text.
- Do not invent skills, technologies, responsibilities, degrees, certifications, years
  of experience, or seniority levels not present in the text.
- Do not infer a `required` importance for something described as optional, and do not
  soften an explicitly mandatory requirement to `preferred` or `optional`.
- If the text does not resemble a job description (e.g. it is empty or unrelated
  content), return `null` for `role_title`, `company`, and `seniority`, and an empty
  `requirements` list.

## Prohibited Behavior

- Do not add requirements that are common for the role in general but not written in
  this specific text.
- Do not output anything other than the JSON object.

## Failure Behavior

If the job description text is empty, unintelligible, or contains no identifiable job
requirements, return a JSON object with `role_title`, `company`, and `seniority` set to
`null` and `requirements` as an empty list, rather than fabricating plausible-looking
requirements.
