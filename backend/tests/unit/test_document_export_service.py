import io

import fitz
from docx import Document as DocxDocument

from app.schemas.resume_version import (
    EducationContent,
    ExperienceContent,
    GeneratedResumeContent,
)
from app.services.document_export_service import generate_docx, generate_pdf

_CONTENT = GeneratedResumeContent(
    professional_summary="Backend engineer focused on API development.",
    experiences=[
        ExperienceContent(
            employer="Acme",
            job_title="Engineer",
            start_date="2020",
            end_date="2023",
            description=None,
            achievements=["Built RESTful APIs using Python and FastAPI."],
        )
    ],
    projects=[],
    skills=[],
    education=[
        EducationContent(
            institution="State University",
            degree="B.S. Computer Science",
            field_of_study=None,
            dates="2016 - 2020",
            achievements=[],
        )
    ],
    certifications=[],
)


def test_generate_docx_includes_all_section_content() -> None:
    docx_bytes = generate_docx(_CONTENT)

    document = DocxDocument(io.BytesIO(docx_bytes))
    text = "\n".join(p.text for p in document.paragraphs)

    assert "Backend engineer focused on API development." in text
    assert "Built RESTful APIs using Python and FastAPI." in text
    assert "B.S. Computer Science, State University" in text


def test_generate_pdf_produces_valid_pdf_with_content() -> None:
    pdf_bytes = generate_pdf(_CONTENT)

    assert pdf_bytes.startswith(b"%PDF")
    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        text = "\n".join(page.get_text() for page in document)

    assert "Built RESTful APIs using Python and FastAPI." in text
