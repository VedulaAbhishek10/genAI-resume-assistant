import pytest

from app.schemas.job import RequirementCategory, RequirementImportance
from app.schemas.matching import GapItem, MatchClassification
from app.services.scoring_service import MatchScoringInput, calculate_match_score, identify_gaps

WEIGHTS = {
    "required_skills": 0.30,
    "experience_alignment": 0.25,
    "responsibility_alignment": 0.20,
    "preferred_skills": 0.10,
    "education_certifications": 0.05,
    "semantic_evidence_quality": 0.10,
}


def _match(
    category: RequirementCategory,
    importance: RequirementImportance,
    classification: MatchClassification,
    confidence: float,
) -> MatchScoringInput:
    return MatchScoringInput(
        category=category,
        importance=importance,
        classification=classification,
        confidence=confidence,
    )


def test_empty_matches_returns_zero_score_and_no_components() -> None:
    overall, components = calculate_match_score([], WEIGHTS)

    assert overall == 0.0
    assert components == {}


def test_all_strong_matches_yields_perfect_score() -> None:
    matches = [
        _match(
            RequirementCategory.SKILL,
            RequirementImportance.REQUIRED,
            MatchClassification.STRONG_MATCH,
            1.0,
        ),
        _match(
            RequirementCategory.EXPERIENCE,
            RequirementImportance.REQUIRED,
            MatchClassification.STRONG_MATCH,
            1.0,
        ),
    ]

    overall, components = calculate_match_score(matches, WEIGHTS)

    assert overall == pytest.approx(1.0)
    assert components["required_skills"] == pytest.approx(1.0)
    assert components["experience_alignment"] == pytest.approx(1.0)
    assert components["semantic_evidence_quality"] == pytest.approx(1.0)


def test_mixed_classifications_produce_expected_component_averages() -> None:
    matches = [
        _match(
            RequirementCategory.SKILL,
            RequirementImportance.REQUIRED,
            MatchClassification.STRONG_MATCH,
            0.9,
        ),
        _match(
            RequirementCategory.SKILL,
            RequirementImportance.PREFERRED,
            MatchClassification.PARTIAL_MATCH,
            0.6,
        ),
        _match(
            RequirementCategory.EXPERIENCE,
            RequirementImportance.REQUIRED,
            MatchClassification.STRONG_MATCH,
            0.8,
        ),
        _match(
            RequirementCategory.RESPONSIBILITY,
            RequirementImportance.REQUIRED,
            MatchClassification.NO_EVIDENCE,
            0.7,
        ),
        _match(
            RequirementCategory.EDUCATION,
            RequirementImportance.REQUIRED,
            MatchClassification.STRONG_MATCH,
            0.95,
        ),
        _match(
            RequirementCategory.DOMAIN_KNOWLEDGE,
            RequirementImportance.OPTIONAL,
            MatchClassification.PARTIAL_MATCH,
            0.5,
        ),
    ]

    overall, components = calculate_match_score(matches, WEIGHTS)

    assert components["required_skills"] == pytest.approx(1.0)
    assert components["preferred_skills"] == pytest.approx(0.5)
    assert components["experience_alignment"] == pytest.approx(1.0)
    assert components["responsibility_alignment"] == pytest.approx(0.0)
    assert components["education_certifications"] == pytest.approx(1.0)
    # domain_knowledge has no dedicated bucket; only affects semantic_evidence_quality.
    assert "domain_knowledge" not in components
    expected_confidence_avg = (0.9 + 0.6 + 0.8 + 0.7 + 0.95 + 0.5) / 6
    assert components["semantic_evidence_quality"] == pytest.approx(expected_confidence_avg)

    expected_overall = (
        0.30 * 1.0
        + 0.25 * 1.0
        + 0.20 * 0.0
        + 0.10 * 0.5
        + 0.05 * 1.0
        + 0.10 * expected_confidence_avg
    )
    assert overall == pytest.approx(expected_overall)


def test_missing_bucket_is_excluded_and_remaining_weights_renormalized() -> None:
    # No education/certification requirements at all in this job description.
    matches = [
        _match(
            RequirementCategory.SKILL,
            RequirementImportance.REQUIRED,
            MatchClassification.STRONG_MATCH,
            1.0,
        ),
    ]

    overall, components = calculate_match_score(matches, WEIGHTS)

    assert "education_certifications" not in components
    # Only required_skills (0.30) and semantic_evidence_quality (0.10) are active;
    # renormalized: required_skills weight share = 0.30 / 0.40 = 0.75
    expected_overall = (0.30 * 1.0 + 0.10 * 1.0) / (0.30 + 0.10)
    assert overall == pytest.approx(expected_overall)
    assert overall == pytest.approx(1.0)


def _gap_candidate(
    importance: RequirementImportance, classification: MatchClassification, text: str
) -> GapItem:
    return GapItem(
        requirement_text=text,
        category=RequirementCategory.SKILL,
        importance=importance,
        classification=classification,
    )


def test_identify_gaps_flags_no_evidence_regardless_of_importance() -> None:
    candidates = [
        _gap_candidate(RequirementImportance.REQUIRED, MatchClassification.NO_EVIDENCE, "a"),
        _gap_candidate(RequirementImportance.OPTIONAL, MatchClassification.NO_EVIDENCE, "b"),
    ]

    gaps = identify_gaps(candidates)

    assert {gap.requirement_text for gap in gaps} == {"a", "b"}


def test_identify_gaps_flags_partial_match_only_when_required() -> None:
    candidates = [
        _gap_candidate(
            RequirementImportance.REQUIRED, MatchClassification.PARTIAL_MATCH, "required-partial"
        ),
        _gap_candidate(
            RequirementImportance.PREFERRED, MatchClassification.PARTIAL_MATCH, "preferred-partial"
        ),
        _gap_candidate(
            RequirementImportance.OPTIONAL, MatchClassification.PARTIAL_MATCH, "optional-partial"
        ),
    ]

    gaps = identify_gaps(candidates)

    assert [gap.requirement_text for gap in gaps] == ["required-partial"]


def test_identify_gaps_excludes_strong_matches() -> None:
    candidates = [
        _gap_candidate(RequirementImportance.REQUIRED, MatchClassification.STRONG_MATCH, "strong"),
    ]

    assert identify_gaps(candidates) == []
