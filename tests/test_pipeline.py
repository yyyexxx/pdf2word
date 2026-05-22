import os
import tempfile
import fitz
from src.core.pipeline import Pipeline, READERS, WRITERS


def _make_sample_pdf(path: str):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Sample PDF text", fontsize=12, fontname="helv")
    doc.save(path)
    doc.close()


def test_pipeline_pdf_to_docx():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name
    try:
        _make_sample_pdf(pdf_path)

        pipeline = Pipeline()
        result = pipeline.convert([pdf_path], ".docx")

        assert result.success_count == 1
        assert result.fail_count == 0
        output = result.results[0].output_path
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0
        os.unlink(output)
    finally:
        os.unlink(pdf_path)


def test_pipeline_unsupported_format():
    pipeline = Pipeline()
    result = pipeline.convert(["nonexistent.xyz"], ".docx")
    assert result.success_count == 0
    assert result.fail_count == 1


def test_detect_format():
    assert Pipeline.detect_format("test.pdf") == ".pdf"
    assert Pipeline.detect_format("test.png") == ".png"
    assert Pipeline.detect_format("test.docx") == ".docx"


def test_available_targets():
    targets = Pipeline.available_targets(".pdf")
    assert ".docx" in targets


def test_registry():
    assert ".pdf" in READERS
    assert ".docx" in WRITERS
