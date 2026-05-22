from src.core.model import Document, Page, TextElement, ImageElement, TableRegion, Rect, SemanticHint


def test_document_empty():
    doc = Document()
    assert len(doc.pages) == 0
    assert doc.metadata == {}


def test_page_with_text_element():
    te = TextElement(
        bbox=Rect(10, 20, 100, 15),
        element_type="text",
        text="Hello",
        font_name="Arial",
        font_size=12,
        font_color="#FF0000",
        bold=True,
        italic=False,
    )
    page = Page(page_number=0, width=612, height=792, elements=[te])
    doc = Document(pages=[page], metadata={"title": "Test"})
    assert len(doc.pages) == 1
    assert doc.pages[0].elements[0].text == "Hello"
    assert doc.pages[0].elements[0].bold is True


def test_text_element_with_hint():
    te = TextElement(
        bbox=Rect(0, 0, 100, 20),
        element_type="text",
        text="Chapter 1",
        font_size=24,
        hint=SemanticHint(role="heading", level=1, confidence=0.95),
    )
    assert te.hint.role == "heading"
    assert te.hint.level == 1


def test_image_element():
    ie = ImageElement(
        bbox=Rect(50, 50, 200, 150),
        element_type="image",
        image_bytes=b"fake",
        image_format="png",
        width=200,
        height=150,
    )
    assert ie.image_format == "png"
    assert ie.width == 200


def test_table_region():
    tr = TableRegion(
        bbox=Rect(10, 10, 400, 100),
        element_type="table_region",
        rows=[["A", "B"], ["1", "2"]],
    )
    assert len(tr.rows) == 2
    assert tr.rows[0][0] == "A"
