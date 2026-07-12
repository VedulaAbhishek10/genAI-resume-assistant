import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.db.session import DbDep
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationRead,
    ApplicationUpdateRequest,
)
from app.services.application_service import (
    create_application,
    get_application,
    list_applications,
    update_application,
)

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", status_code=201, response_model=ApplicationRead)
async def create(request: ApplicationCreateRequest, db: DbDep) -> ApplicationRead:
    application = await create_application(db, request)
    return ApplicationRead.model_validate(application)


@router.get("", response_model=list[ApplicationRead])
async def list_all(
    db: DbDep, candidate_profile_id: Annotated[uuid.UUID, Query()]
) -> list[ApplicationRead]:
    applications = await list_applications(db, candidate_profile_id)
    return [ApplicationRead.model_validate(application) for application in applications]


@router.get("/{application_id}", response_model=ApplicationRead)
async def get(application_id: uuid.UUID, db: DbDep) -> ApplicationRead:
    application = await get_application(db, application_id)
    return ApplicationRead.model_validate(application)


@router.patch("/{application_id}", response_model=ApplicationRead)
async def update(
    application_id: uuid.UUID, request: ApplicationUpdateRequest, db: DbDep
) -> ApplicationRead:
    application = await update_application(db, application_id, request)
    return ApplicationRead.model_validate(application)
