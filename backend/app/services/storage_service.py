from pathlib import Path
from uuid import UUID

from app.core.config import Settings
from app.core.exceptions import (
    EmptyFileError,
    FileTooLargeError,
    InvalidDocumentError,
    UnsupportedFileTypeError,
)

PDF_EXTENSION = ".pdf"
DOCX_EXTENSION = ".docx"
PDF_SIGNATURE = b"%PDF"
DOCX_SIGNATURE = b"PK\x03\x04"

SUPPORTED_EXTENSIONS = {PDF_EXTENSION, DOCX_EXTENSION}


def extension_for(filename: str) -> str:
    return Path(filename).suffix.lower()


def validate_upload(filename: str, content: bytes, settings: Settings) -> str:
    """Validate an uploaded resume file. Returns the validated extension."""
    extension = extension_for(filename)
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{extension or 'unknown'}'. Only PDF and DOCX are supported."
        )

    if not content:
        raise EmptyFileError("Uploaded file is empty.")

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size_bytes:
        raise FileTooLargeError(
            f"Uploaded file exceeds the maximum size of {settings.max_upload_size_mb}MB."
        )

    if extension == PDF_EXTENSION and not content.startswith(PDF_SIGNATURE):
        raise InvalidDocumentError("File does not appear to be a valid PDF document.")

    if extension == DOCX_EXTENSION and not content.startswith(DOCX_SIGNATURE):
        raise InvalidDocumentError("File does not appear to be a valid DOCX document.")

    return extension


def resume_dir_for(resume_id: UUID, settings: Settings) -> Path:
    resume_dir = Path(settings.upload_storage_dir) / str(resume_id)
    resume_dir.mkdir(parents=True, exist_ok=True)
    return resume_dir


def save_resume_file(resume_id: UUID, extension: str, content: bytes, settings: Settings) -> Path:
    file_path = resume_dir_for(resume_id, settings) / f"original{extension}"
    file_path.write_bytes(content)
    return file_path


def save_extracted_text(resume_id: UUID, text: str, settings: Settings) -> Path:
    file_path = resume_dir_for(resume_id, settings) / "extracted.txt"
    file_path.write_text(text, encoding="utf-8")
    return file_path
