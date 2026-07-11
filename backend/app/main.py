from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.resumes import router as resumes_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings)

app = FastAPI(title=settings.app_name)
app.include_router(resumes_router, prefix="/api/v1")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.error_code, "message": exc.message}},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
