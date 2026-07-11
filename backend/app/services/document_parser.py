import io
import re

import fitz
from docx import Document
from docx.opc.exceptions import PackageNotFoundError

from app.core.exceptions import ExtractionError

PDF_EXTENSION = ".pdf"
DOCX_EXTENSION = ".docx"


def _normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_pdf(content: bytes) -> str:
    try:
        with fitz.open(stream=content, filetype="pdf") as document:
            pages_text = [page.get_text() for page in document]
    except Exception as exc:
        raise ExtractionError(f"Failed to extract text from PDF: {exc}") from exc

    text = _normalize("\n".join(pages_text))
    if not text:
        raise ExtractionError("PDF document contains no extractable text.")
    return text


def extract_text_from_docx(content: bytes) -> str:
    try:
        document = Document(io.BytesIO(content))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
    except PackageNotFoundError as exc:
        raise ExtractionError(f"Failed to extract text from DOCX: {exc}") from exc
    except Exception as exc:
        raise ExtractionError(f"Failed to extract text from DOCX: {exc}") from exc

    text = _normalize("\n".join(paragraphs))
    if not text:
        raise ExtractionError("DOCX document contains no extractable text.")
    return text


def extract_text(extension: str, content: bytes) -> str:
    if extension == PDF_EXTENSION:
        return extract_text_from_pdf(content)
    if extension == DOCX_EXTENSION:
        return extract_text_from_docx(content)
    raise ExtractionError(f"Unsupported extension for extraction: '{extension}'.")
