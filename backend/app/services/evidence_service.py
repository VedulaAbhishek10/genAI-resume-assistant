from app.models.candidate import CandidateProfile
from app.models.evidence import CandidateEvidence
from app.schemas.evidence import EvidenceType, SourceEntityType


def generate_evidence(profile: CandidateProfile) -> list[CandidateEvidence]:
    """Deterministically derive atomic, traceable evidence units from a candidate profile.

    Pure function: no LLM calls, no database access. Each unit preserves provenance via
    `source_entity_type`/`source_entity_id` pointing back to the originating row.
    """
    evidence: list[CandidateEvidence] = []

    for experience in profile.experiences:
        metadata = {"employer": experience.employer, "job_title": experience.job_title}
        if experience.description:
            evidence.append(
                CandidateEvidence(
                    candidate_profile_id=profile.id,
                    evidence_type=EvidenceType.EXPERIENCE_BULLET,
                    source_entity_type=SourceEntityType.EXPERIENCE,
                    source_entity_id=experience.id,
                    text=experience.description,
                    evidence_metadata=metadata,
                )
            )
        for achievement in experience.achievements:
            evidence.append(
                CandidateEvidence(
                    candidate_profile_id=profile.id,
                    evidence_type=EvidenceType.ACHIEVEMENT,
                    source_entity_type=SourceEntityType.EXPERIENCE,
                    source_entity_id=experience.id,
                    text=achievement,
                    evidence_metadata=metadata,
                )
            )

    for project in profile.projects:
        metadata = {"name": project.name}
        if project.description:
            evidence.append(
                CandidateEvidence(
                    candidate_profile_id=profile.id,
                    evidence_type=EvidenceType.PROJECT_BULLET,
                    source_entity_type=SourceEntityType.PROJECT,
                    source_entity_id=project.id,
                    text=project.description,
                    evidence_metadata=metadata,
                )
            )
        for achievement in project.achievements:
            evidence.append(
                CandidateEvidence(
                    candidate_profile_id=profile.id,
                    evidence_type=EvidenceType.ACHIEVEMENT,
                    source_entity_type=SourceEntityType.PROJECT,
                    source_entity_id=project.id,
                    text=achievement,
                    evidence_metadata=metadata,
                )
            )

    for skill in profile.skills:
        evidence.append(
            CandidateEvidence(
                candidate_profile_id=profile.id,
                evidence_type=EvidenceType.SKILL,
                source_entity_type=SourceEntityType.SKILL,
                source_entity_id=skill.id,
                text=skill.name,
                evidence_metadata={"category": skill.category},
            )
        )

    for education in profile.education:
        education_metadata: dict[str, str | None] = {
            "institution": education.institution,
            "degree": education.degree,
        }
        summary = f"{education.degree}, {education.institution}" if education.degree else (
            education.institution
        )
        evidence.append(
            CandidateEvidence(
                candidate_profile_id=profile.id,
                evidence_type=EvidenceType.EDUCATION_ITEM,
                source_entity_type=SourceEntityType.EDUCATION,
                source_entity_id=education.id,
                text=summary,
                evidence_metadata=education_metadata,
            )
        )
        for achievement in education.achievements:
            evidence.append(
                CandidateEvidence(
                    candidate_profile_id=profile.id,
                    evidence_type=EvidenceType.ACHIEVEMENT,
                    source_entity_type=SourceEntityType.EDUCATION,
                    source_entity_id=education.id,
                    text=achievement,
                    evidence_metadata=education_metadata,
                )
            )

    for certification in profile.certifications:
        evidence.append(
            CandidateEvidence(
                candidate_profile_id=profile.id,
                evidence_type=EvidenceType.CERTIFICATION,
                source_entity_type=SourceEntityType.CERTIFICATION,
                source_entity_id=certification.id,
                text=certification.name,
                evidence_metadata={
                    "issuing_organization": certification.issuing_organization,
                    "issue_date": certification.issue_date,
                },
            )
        )

    return evidence
