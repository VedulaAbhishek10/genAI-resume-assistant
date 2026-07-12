import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidRequestError, NotFoundError
from app.models.application import Application
from app.models.candidate import CandidateProfile
from app.models.job import JobDescription
from app.models.resume_version import ResumeVersion
from app.schemas.application import ApplicationCreateRequest, ApplicationUpdateRequest


async def _validate_resume_version(
    db: AsyncSession, resume_version_id: uuid.UUID, job_description_id: uuid.UUID
) -> None:
    resume_version = await db.get(ResumeVersion, resume_version_id)
    if resume_version is None:
        raise NotFoundError(f"Resume version '{resume_version_id}' was not found.")
    if resume_version.job_description_id != job_description_id:
        raise InvalidRequestError(
            f"Resume version '{resume_version_id}' was not generated for job "
            f"description '{job_description_id}'."
        )


async def create_application(
    db: AsyncSession, request: ApplicationCreateRequest
) -> Application:
    candidate_profile = await db.get(CandidateProfile, request.candidate_profile_id)
    if candidate_profile is None:
        raise NotFoundError(
            f"Candidate profile '{request.candidate_profile_id}' was not found."
        )

    job_description = await db.get(JobDescription, request.job_description_id)
    if job_description is None:
        raise NotFoundError(f"Job description '{request.job_description_id}' was not found.")

    if request.resume_version_id is not None:
        await _validate_resume_version(
            db, request.resume_version_id, request.job_description_id
        )

    application = Application(
        id=uuid.uuid4(),
        candidate_profile_id=request.candidate_profile_id,
        job_description_id=request.job_description_id,
        resume_version_id=request.resume_version_id,
        company=request.company if request.company is not None else job_description.company,
        role=request.role if request.role is not None else job_description.role_title,
        notes=request.notes,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application, attribute_names=["created_at"])
    return application


async def list_applications(
    db: AsyncSession, candidate_profile_id: uuid.UUID
) -> list[Application]:
    result = await db.execute(
        select(Application)
        .where(Application.candidate_profile_id == candidate_profile_id)
        .order_by(Application.created_at)
    )
    return list(result.scalars().all())


async def get_application(db: AsyncSession, application_id: uuid.UUID) -> Application:
    application = await db.get(Application, application_id)
    if application is None:
        raise NotFoundError(f"Application '{application_id}' was not found.")
    return application


async def update_application(
    db: AsyncSession, application_id: uuid.UUID, request: ApplicationUpdateRequest
) -> Application:
    application = await get_application(db, application_id)

    if request.resume_version_id is not None:
        await _validate_resume_version(
            db, request.resume_version_id, application.job_description_id
        )
        application.resume_version_id = request.resume_version_id

    if request.status is not None:
        application.status = request.status
    if request.notes is not None:
        application.notes = request.notes
    if request.application_date is not None:
        application.application_date = request.application_date

    await db.commit()
    await db.refresh(
        application,
        attribute_names=["status", "notes", "application_date", "resume_version_id"],
    )
    return application
