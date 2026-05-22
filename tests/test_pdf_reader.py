import os
import tempfile
import fitz
from src.core.readers.pdf_reader import PDFReader
from src.core.model import TextElement, ImageElement


def _make_sample_pdf(path: str):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello World", fontsize=12, fontname="helv")
    page.insert_text((72, 100), "Title Text", fontsize=24, fontname="helv")
    doc.save(path)
    doc.close()


def test_pdf_reader_basic():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        tmp = f.name
    try:
        _make_sample_pdf(tmp)
        reader = PDFReader()
        doc = reader.read(tmp)
        assert len(doc.pages) == 1
        texts = [e for e in doc.pages[0].elements if isinstance(e, TextElement)]
        assert len(texts) >= 2
    finally:
        os.unlink(tmp)


def test_pdf_reader_metadata():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        tmp = f.name
    try:
        _make_sample_pdf(tmp)
        reader = PDFReader()
        doc = reader.read(tmp)
        assert isinstance(doc.metadata, dict)
    finally:
        os.unlink(tmp)


def test_pdf_reader_supported_extensions():
    assert ".pdf" in PDFReader.supported_extensions()
