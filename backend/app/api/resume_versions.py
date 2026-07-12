import uuid

from fastapi import APIRouter, Response

from app.core.exceptions import NotFoundError
from app.db.session import DbDep
from app.models.resume import Resume
from app.schemas.resume_version import (
    GeneratedResumeContent,
    ResumeVersionCreateRequest,
    ResumeVersionRead,
)
from app.services.document_export_service import generate_docx, generate_pdf
from app.services.resume_version_service import (
    create_resume_version,
    get_resume_version,
    list_resume_versions,
)

router = APIRouter(tags=["resume-versions"])


@router.post(
    "/resumes/{resume_id}/versions",
    status_code=201,
    response_model=ResumeVersionRead,
)
async def create_version(
    resume_id: uuid.UUID, request: ResumeVersionCreateRequest, db: DbDep
) -> ResumeVersionRead:
    resume_version = await create_resume_version(db, resume_id, request.match_analysis_id)
    return ResumeVersionRead.model_validate(resume_version)


@router.get(
    "/resumes/{resume_id}/versions",
    response_model=list[ResumeVersionRead],
)
async def list_versions(resume_id: uuid.UUID, db: DbDep) -> list[ResumeVersionRead]:
    resume = await db.get(Resume, resume_id)
    if resume is None:
        raise NotFoundError(f"Resume '{resume_id}' was not found.")

    resume_versions = await list_resume_versions(db, resume_id)
    return [ResumeVersionRead.model_validate(version) for version in resume_versions]


@router.get(
    "/resume-versions/{resume_version_id}",
    response_model=ResumeVersionRead,
)
async def get_version(resume_version_id: uuid.UUID, db: DbDep) -> ResumeVersionRead:
    resume_version = await get_resume_version(db, resume_version_id)
    return ResumeVersionRead.model_validate(resume_version)


@router.get("/resume-versions/{resume_version_id}/export/docx")
async def export_version_docx(resume_version_id: uuid.UUID, db: DbDep) -> Response:
    resume_version = await get_resume_version(db, resume_version_id)
    content = GeneratedResumeContent.model_validate(resume_version.generated_content)
    docx_bytes = generate_docx(content)
    return Response(
        content=docx_bytes,
        media_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        headers={
            "Content-Disposition": f'attachment; filename="resume-{resume_version_id}.docx"'
        },
    )


@router.get("/resume-versions/{resume_version_id}/export/pdf")
async def export_version_pdf(resume_version_id: uuid.UUID, db: DbDep) -> Response:
    resume_version = await get_resume_version(db, resume_version_id)
    content = GeneratedResumeContent.model_validate(resume_version.generated_content)
    pdf_bytes = generate_pdf(content)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="resume-{resume_version_id}.pdf"'
        },
    )
