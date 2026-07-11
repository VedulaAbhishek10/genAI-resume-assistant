"""Retrieval quality evaluation (see docs/EVALUATION.md).

Measures recall@K for semantic evidence retrieval against a small, synthetic,
hand-labeled dataset: for each (job_requirement_text, expected_evidence_text) pair,
checks whether the expected evidence appears in the top-K results retrieved for that
requirement. Unlike unit/integration tests, this measures AI *quality* rather than
correctness of deterministic logic — but is fast and deterministic enough (fixed local
embedding model, fixed inputs) to run as part of the standard test suite.
"""

import uuid
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.candidate import CandidateProfile
from app.models.evidence import CandidateEvidence
from app.services.embedding_service import embed_texts_async
from app.services.retrieval_service import retrieve_relevant_evidence

EVIDENCE_TEXTS = [
    "Deployed and managed Kubernetes clusters for production workloads.",
    "Built RESTful APIs using FastAPI and Python.",
    "Designed relational database schemas in PostgreSQL.",
    "Implemented CI/CD pipelines using GitHub Actions.",
    "Trained and fine-tuned transformer-based NLP models.",
    "Led a team of 5 engineers on a customer-facing product launch.",
    "Wrote unit and integration tests achieving 90% code coverage.",
    "Migrated a monolithic application to a microservices architecture.",
    "Presented quarterly technical roadmaps to executive stakeholders.",
    "Volunteered teaching coding basics to high school students.",
]

# (job_requirement_text, expected_evidence_text) — expected_evidence_text must be an
# exact entry from EVIDENCE_TEXTS above.
LABELED_QUERIES = [
    ("Experience with container orchestration platforms", EVIDENCE_TEXTS[0]),
    ("Experience building backend APIs with Python", EVIDENCE_TEXTS[1]),
    ("Strong SQL and relational database design skills", EVIDENCE_TEXTS[2]),
    ("Experience with CI/CD and DevOps automation", EVIDENCE_TEXTS[3]),
    ("Experience with machine learning and natural language processing", EVIDENCE_TEXTS[4]),
    ("Experience leading and managing engineering teams", EVIDENCE_TEXTS[5]),
    ("Strong software testing and quality assurance practices", EVIDENCE_TEXTS[6]),
    ("Experience with microservices architecture", EVIDENCE_TEXTS[7]),
]

TOP_K = 3
MINIMUM_ACCEPTABLE_RECALL = 0.75


@pytest.fixture
async def seeded_profile_id() -> AsyncGenerator[uuid.UUID]:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    profile_id = uuid.uuid4()
    embeddings = await embed_texts_async(EVIDENCE_TEXTS, settings)

    async with session_factory() as session:
        profile = CandidateProfile(id=profile_id)
        profile.evidence = [
            CandidateEvidence(
                id=uuid.uuid4(),
                candidate_profile_id=profile_id,
                evidence_type="achievement",
                source_entity_type="experience",
                source_entity_id=uuid.uuid4(),
                text=text,
                evidence_metadata={},
                embedding=embedding,
            )
            for text, embedding in zip(EVIDENCE_TEXTS, embeddings, strict=True)
        ]
        session.add(profile)
        await session.commit()

    yield profile_id
    await engine.dispose()


async def test_retrieval_recall_at_k_meets_minimum_threshold(
    seeded_profile_id: uuid.UUID,
) -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    hits = 0
    async with session_factory() as db:
        for requirement_text, expected_text in LABELED_QUERIES:
            results = await retrieve_relevant_evidence(
                db, seeded_profile_id, requirement_text, settings, top_k=TOP_K
            )
            retrieved_texts = {evidence.text for evidence, _distance in results}
            if expected_text in retrieved_texts:
                hits += 1

    await engine.dispose()

    recall_at_k = hits / len(LABELED_QUERIES)
    print(
        f"\n[retrieval evaluation] recall@{TOP_K} = {recall_at_k:.2f} "
        f"({hits}/{len(LABELED_QUERIES)} examples) "
        f"model={settings.embedding_model}"
    )

    assert recall_at_k >= MINIMUM_ACCEPTABLE_RECALL
