import os
import tempfile
from src.core.model import Document, Page, TextElement, ImageElement, TableRegion, Rect, SemanticHint
from src.core.writers.docx_writer import DocxWriter


def test_docx_writer_text():
    page = Page(page_number=0, width=612, height=792, elements=[
        TextElement(
            bbox=Rect(10, 10, 200, 14),
            element_type="text",
            text="Hello DOCX",
            font_name="Arial",
            font_size=12,
        ),
    ])
    doc = Document(pages=[page])

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        tmp = f.name
    try:
        writer = DocxWriter()
        writer.write(doc, tmp)
        assert os.path.getsize(tmp) > 0
    finally:
        os.unlink(tmp)


def test_docx_writer_heading():
    page = Page(page_number=0, width=612, height=792, elements=[
        TextElement(
            bbox=Rect(10, 10, 200, 28),
            element_type="text",
            text="Chapter Title",
            font_size=24,
            hint=SemanticHint(role="heading", level=1, confidence=0.95),
        ),
        TextElement(
            bbox=Rect(10, 50, 200, 14),
            element_type="text",
            text="Body text here.",
            font_size=12,
            hint=SemanticHint(role="paragraph", confidence=0.8),
        ),
    ])
    doc = Document(pages=[page])

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        tmp = f.name
    try:
        writer = DocxWriter()
        writer.write(doc, tmp)
        assert os.path.getsize(tmp) > 0
    finally:
        os.unlink(tmp)


def test_docx_writer_table():
    page = Page(page_number=0, width=612, height=792, elements=[
        TableRegion(
            bbox=Rect(10, 10, 400, 100),
            element_type="table_region",
            rows=[["Name", "Age"], ["Alice", "30"]],
        ),
    ])
    doc = Document(pages=[page])

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        tmp = f.name
    try:
        writer = DocxWriter()
        writer.write(doc, tmp)
        assert os.path.getsize(tmp) > 0
    finally:
        os.unlink(tmp)
