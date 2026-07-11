from collections import defaultdict

from pydantic import BaseModel

from app.schemas.job import RequirementCategory, RequirementImportance
from app.schemas.matching import GapItem, MatchClassification

CLASSIFICATION_SCORES: dict[MatchClassification, float] = {
    MatchClassification.STRONG_MATCH: 1.0,
    MatchClassification.PARTIAL_MATCH: 0.5,
    MatchClassification.NO_EVIDENCE: 0.0,
}


class MatchScoringInput(BaseModel):
    category: RequirementCategory
    importance: RequirementImportance
    classification: MatchClassification
    confidence: float


def _bucket_for(category: RequirementCategory, importance: RequirementImportance) -> str | None:
    if category == RequirementCategory.SKILL and importance == RequirementImportance.REQUIRED:
        return "required_skills"
    if category == RequirementCategory.SKILL and importance == RequirementImportance.PREFERRED:
        return "preferred_skills"
    if category == RequirementCategory.EXPERIENCE:
        return "experience_alignment"
    if category == RequirementCategory.RESPONSIBILITY:
        return "responsibility_alignment"
    if category in (RequirementCategory.EDUCATION, RequirementCategory.CERTIFICATION):
        return "education_certifications"
    # RequirementCategory.DOMAIN_KNOWLEDGE and optional-importance skills have no
    # dedicated weighted bucket (see docs/ROADMAP.md M5.3); they still influence
    # `semantic_evidence_quality` via their confidence contribution below.
    return None


def calculate_match_score(
    matches: list[MatchScoringInput],
    weights: dict[str, float],
) -> tuple[float, dict[str, float]]:
    """Deterministically compute component and overall match scores.

    LLMs classify individual requirement-evidence relationships (see
    matching_service.py); this function performs the final scoring itself, per
    ADR-007. Each classification maps to a fixed numeric score
    (CLASSIFICATION_SCORES); component scores are the average of that mapped score
    across the requirements in each bucket. Buckets with no requirements are
    excluded and the remaining weights are renormalized, so a job description with
    (for example) no certification requirements does not get penalized for lacking
    one.

    Returns (overall_score, component_scores). If there are no matches at all,
    returns (0.0, {}).
    """
    if not matches:
        return 0.0, {}

    bucket_scores: dict[str, list[float]] = defaultdict(list)
    confidences: list[float] = []

    for match in matches:
        bucket = _bucket_for(match.category, match.importance)
        mapped_score = CLASSIFICATION_SCORES[match.classification]
        if bucket is not None:
            bucket_scores[bucket].append(mapped_score)
        confidences.append(match.confidence)

    component_scores: dict[str, float] = {
        bucket: sum(scores) / len(scores) for bucket, scores in bucket_scores.items()
    }
    component_scores["semantic_evidence_quality"] = sum(confidences) / len(confidences)

    active_weights = {
        component: weight for component, weight in weights.items() if component in component_scores
    }
    total_weight = sum(active_weights.values())
    if total_weight == 0:
        return 0.0, component_scores

    overall_score = (
        sum(component_scores[component] * weight for component, weight in active_weights.items())
        / total_weight
    )
    return overall_score, component_scores


def identify_gaps(candidates: list[GapItem]) -> list[GapItem]:
    """Identify genuine gaps: missing evidence, or a weak match on a required item.

    A `NO_EVIDENCE` classification is always a gap. A `PARTIAL_MATCH` is only
    surfaced as a gap when the requirement is `required` — a partial match on a
    merely `preferred` or `optional` item is not a pressing gap worth flagging
    distinctly from a solid match (see docs/ROADMAP.md M5.4).
    """
    return [
        candidate
        for candidate in candidates
        if candidate.classification == MatchClassification.NO_EVIDENCE
        or (
            candidate.classification == MatchClassification.PARTIAL_MATCH
            and candidate.importance == RequirementImportance.REQUIRED
        )
    ]
