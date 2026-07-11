from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.llm.base import LLMClient
from app.llm.provider import get_llm_client
from app.schemas.resume import ResumeUploadResponse
from app.services.document_parser import extract_text
from app.services.profile_persistence import persist_resume_and_profile
from app.services.resume_parser import extract_candidate_profile
from app.services.storage_service import save_extracted_text, save_resume_file, validate_upload

router = APIRouter(prefix="/resumes", tags=["resumes"])

_CONTENT_TYPE_FOR_EXTENSION = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbDep = Annotated[AsyncSession, Depends(get_db)]


def _llm_client_dependency(settings: SettingsDep) -> LLMClient:
    return get_llm_client(settings)


LLMClientDep = Annotated[LLMClient, Depends(_llm_client_dependency)]


@router.post("", status_code=201, response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile,
    settings: SettingsDep,
    llm_client: LLMClientDep,
    db: DbDep,
) -> ResumeUploadResponse:
    content = await file.read()
    extension = validate_upload(file.filename or "", content, settings)

    resume_id = uuid4()
    save_resume_file(resume_id, extension, content, settings)

    extracted_text = extract_text(extension, content)
    save_extracted_text(resume_id, extracted_text, settings)

    candidate_profile = await extract_candidate_profile(extracted_text, llm_client)

    filename = file.filename or f"resume{extension}"
    await persist_resume_and_profile(
        db,
        resume_id=resume_id,
        filename=filename,
        document_type=extension.lstrip("."),
        extracted_text=extracted_text,
        profile=candidate_profile,
    )

    return ResumeUploadResponse(
        id=resume_id,
        filename=filename,
        content_type=_CONTENT_TYPE_FOR_EXTENSION[extension],
        size_bytes=len(content),
        status="uploaded",
        extracted_text=extracted_text,
        candidate_profile=candidate_profile,
    )
