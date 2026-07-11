import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobDescription, JobRequirement
from app.schemas.job import JobRequirementExtraction


async def persist_job_description(
    db: AsyncSession,
    source_text: str,
    extraction: JobRequirementExtraction,
) -> JobDescription:
    job_description = JobDescription(
        id=uuid.uuid4(),
        source_text=source_text,
        role_title=extraction.role_title,
        company=extraction.company,
        seniority=extraction.seniority,
        requirements=[
            JobRequirement(
                id=uuid.uuid4(),
                text=item.text,
                category=item.category,
                importance=item.importance,
            )
            for item in extraction.requirements
        ],
    )

    db.add(job_description)
    await db.commit()
    # Scope the refresh to the server-generated column only: a bare refresh() also
    # expires relationships, which would force an async-unsafe lazy load the next
    # time `requirements` is accessed (e.g. during Pydantic serialization).
    await db.refresh(job_description, attribute_names=["created_at"])
    return job_description
