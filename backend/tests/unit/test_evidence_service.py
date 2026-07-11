import uuid

from app.models.candidate import (
    CandidateProfile,
    Certification,
    Education,
    Experience,
    Project,
    Skill,
)
from app.schemas.evidence import EvidenceType, SourceEntityType
from app.services.evidence_service import generate_evidence


def _build_profile() -> CandidateProfile:
    profile_id = uuid.uuid4()
    experience = Experience(
        id=uuid.uuid4(),
        employer="Example Corp",
        job_title="Senior Engineer",
        description="Led backend development.",
        achievements=["Reduced latency by 30%", "Mentored 2 engineers"],
    )
    project = Project(
        id=uuid.uuid4(),
        name="Internal Tools",
        description="Built internal tooling.",
        achievements=["Automated deployment pipeline"],
    )
    skill = Skill(id=uuid.uuid4(), name="Python", category="Programming")
    education = Education(
        id=uuid.uuid4(),
        institution="Example University",
        degree="B.S. Computer Science",
        achievements=["Dean's list"],
    )
    certification = Certification(
        id=uuid.uuid4(), name="AWS Certified", issuing_organization="AWS"
    )

    profile = CandidateProfile(
        id=profile_id,
        professional_summary="Experienced engineer.",
        experiences=[experience],
        projects=[project],
        skills=[skill],
        education=[education],
        certifications=[certification],
    )
    return profile


def test_generate_evidence_produces_one_unit_per_atomic_claim() -> None:
    profile = _build_profile()

    evidence = generate_evidence(profile)

    texts = {item.text for item in evidence}
    assert "Led backend development." in texts
    assert "Reduced latency by 30%" in texts
    assert "Mentored 2 engineers" in texts
    assert "Built internal tooling." in texts
    assert "Automated deployment pipeline" in texts
    assert "Python" in texts
    assert "B.S. Computer Science, Example University" in texts
    assert "Dean's list" in texts
    assert "AWS Certified" in texts

    # 3 (experience: description + 2 achievements) + 2 (project: description + achievement)
    # + 1 (skill) + 2 (education: summary + achievement) + 1 (certification)
    assert len(evidence) == 9


def test_generate_evidence_preserves_provenance() -> None:
    profile = _build_profile()
    experience = profile.experiences[0]

    evidence = generate_evidence(profile)

    experience_items = [item for item in evidence if item.source_entity_id == experience.id]
    assert len(experience_items) == 3  # description + 2 achievements
    for item in experience_items:
        assert item.source_entity_type == SourceEntityType.EXPERIENCE
        assert item.candidate_profile_id == profile.id
        assert item.evidence_metadata["employer"] == "Example Corp"

    achievement_items = [
        item for item in evidence if item.evidence_type == EvidenceType.ACHIEVEMENT
    ]
    assert len(achievement_items) == 4  # 2 experience + 1 project + 1 education


def test_generate_evidence_does_not_fabricate_missing_description() -> None:
    profile = CandidateProfile(
        id=uuid.uuid4(),
        experiences=[
            Experience(
                id=uuid.uuid4(), employer="Acme", job_title="Engineer", achievements=[]
            )
        ],
    )

    evidence = generate_evidence(profile)

    assert evidence == []
