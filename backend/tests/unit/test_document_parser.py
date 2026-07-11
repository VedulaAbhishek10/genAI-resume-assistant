from pathlib import Path

import pytest

from app.core.exceptions import ExtractionError
from app.services.document_parser import (
    extract_text,
    extract_text_from_docx,
    extract_text_from_pdf,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_extract_text_from_pdf_returns_normalized_text() -> None:
    content = (FIXTURES / "sample_resume.pdf").read_bytes()

    text = extract_text_from_pdf(content)

    assert "Jordan Sample" in text
    assert "Software Engineer" in text
    assert "\r" not in text


def test_extract_text_from_docx_returns_normalized_text() -> None:
    content = (FIXTURES / "sample_resume.docx").read_bytes()

    text = extract_text_from_docx(content)

    assert "Jordan Sample" in text
    assert "Senior Engineer at Example Corp" in text


def test_extract_text_dispatches_by_extension() -> None:
    pdf_content = (FIXTURES / "sample_resume.pdf").read_bytes()
    docx_content = (FIXTURES / "sample_resume.docx").read_bytes()

    assert "Jordan Sample" in extract_text(".pdf", pdf_content)
    assert "Jordan Sample" in extract_text(".docx", docx_content)


def test_extract_text_from_corrupt_pdf_raises_extraction_error() -> None:
    content = (FIXTURES / "corrupt.pdf").read_bytes()

    with pytest.raises(ExtractionError):
        extract_text_from_pdf(content)


def test_extract_text_from_corrupt_docx_raises_extraction_error() -> None:
    with pytest.raises(ExtractionError):
        extract_text_from_docx(b"not a real docx file")


def test_extract_text_unsupported_extension_raises() -> None:
    with pytest.raises(ExtractionError):
        extract_text(".txt", b"some content")
