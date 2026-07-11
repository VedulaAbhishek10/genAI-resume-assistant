from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.analysis import router as analysis_router
from app.api.evidence import router as evidence_router
from app.api.jobs import router as jobs_router
from app.api.resumes import router as resumes_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings)

app = FastAPI(title=settings.app_name)
app.include_router(resumes_router, prefix="/api/v1")
app.include_router(evidence_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.error_code, "message": exc.message}},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    message = "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in exc.errors()
    )
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": message or "Invalid request."}},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
