from src.core.model import Document, Page, TextElement, TableRegion, Rect, SemanticHint
from src.inference.infer import infer
from src.inference.paragraph import merge_paragraphs
from src.inference.heading import detect_headings
from src.inference.table import detect_tables, _is_grid


def _make_page(texts: list[tuple[str, float, float]]) -> Page:
    """Helper: create a page with TextElements at given (x, y) and font_size=12."""
    elements = []
    for text, x, y in texts:
        te = TextElement(
            bbox=Rect(x, y, len(text) * 6, 14),
            element_type="text",
            text=text,
            font_size=12,
        )
        elements.append(te)
    return Page(page_number=0, width=612, height=792, elements=elements)


def test_merge_paragraphs_same_line():
    """Two nearby text spans on same line should merge."""
    page = _make_page([
        ("Hello", 10, 100),
        ("World", 70, 100),  # close, same y
    ])
    merge_paragraphs([page])
    texts = [e for e in page.elements if hasattr(e, 'text')]
    assert len(texts) == 1
    assert "Hello" in texts[0].text and "World" in texts[0].text


def test_merge_paragraphs_next_line():
    """Two spans on adjacent lines within bbox should merge."""
    page = _make_page([
        ("Line one", 10, 100),
        ("Line two", 10, 115),
    ])
    merge_paragraphs([page])
    texts = [e for e in page.elements if hasattr(e, 'text')]
    assert len(texts) == 1
    assert "\n" in texts[0].text


def test_merge_paragraphs_no_merge_far():
    """Two spans far apart should not merge."""
    page = _make_page([
        ("Top", 10, 100),
        ("Bottom", 10, 300),
    ])
    merge_paragraphs([page])
    texts = [e for e in page.elements if hasattr(e, 'text')]
    assert len(texts) == 2


def test_detect_headings():
    """Larger font text should be detected as heading."""
    page = Page(page_number=0, width=612, height=792, elements=[
        TextElement(
            bbox=Rect(10, 10, 200, 30),
            element_type="text", text="Title", font_size=28,
        ),
        TextElement(
            bbox=Rect(10, 50, 200, 14),
            element_type="text", text="Body text", font_size=12,
        ),
        TextElement(
            bbox=Rect(10, 80, 200, 14),
            element_type="text", text="More body", font_size=11,
        ),
    ])
    detect_headings([page])
    title_el = page.elements[0]
    assert title_el.hint is not None
    assert title_el.hint.role == "heading"


def test_infer_pipeline():
    """Full inference pipeline runs on a multi-element page."""
    page = Page(page_number=0, width=612, height=792, elements=[
        TextElement(
            bbox=Rect(10, 10, 200, 30),
            element_type="text", text="Chapter 1", font_size=24,
        ),
        TextElement(
            bbox=Rect(10, 50, 200, 14),
            element_type="text", text="First paragraph", font_size=12,
        ),
        TextElement(
            bbox=Rect(10, 70, 200, 14),
            element_type="text", text="Second line", font_size=12,
        ),
    ])
    doc = Document(pages=[page])
    result = infer(doc)
    assert result is doc
    # heading should be detected on the large-font element
    assert doc.pages[0].elements[0].hint.role == "heading"


def test_heading_numbering_pattern():
    """Numbered headings should be detected."""
    page = Page(page_number=0, width=612, height=792, elements=[
        TextElement(
            bbox=Rect(10, 10, 200, 30),
            element_type="text", text="1.1 概述", font_size=24,
        ),
        TextElement(
            bbox=Rect(10, 50, 200, 14),
            element_type="text", text="Body text", font_size=12,
        ),
    ])
    detect_headings([page])
    assert page.elements[0].hint is not None
    assert page.elements[0].hint.role == "heading"


def test_bold_heading_detection():
    """Bold text with slightly larger size should score higher."""
    page = Page(page_number=0, width=612, height=792, elements=[
        TextElement(
            bbox=Rect(10, 10, 200, 18),
            element_type="text", text="Section", font_size=16, bold=True,
        ),
        TextElement(
            bbox=Rect(10, 40, 200, 14),
            element_type="text", text="Normal", font_size=12,
        ),
    ])
    detect_headings([page])
    assert page.elements[0].hint is not None
    assert page.elements[0].hint.role == "heading"


def test_table_detection_grid():
    """Grid-aligned text should be detected as table."""
    cells = [
        TextElement(
            bbox=Rect(x, y, 80, 14),
            element_type="text", text=f"({r},{c})", font_size=11,
        )
        for r, y in enumerate([100, 118, 136])
        for c, x in enumerate([50, 140, 230])
    ]
    page = Page(page_number=0, width=612, height=792, elements=cells)
    detect_tables([page])
    tables = [e for e in page.elements if isinstance(e, TableRegion)]
    assert len(tables) == 1
    assert len(tables[0].rows) == 3


def test_is_grid_true():
    """A set of grid-aligned texts should be identified as a grid."""
    texts = [
        TextElement(bbox=Rect(x * 100, y * 30, 90, 14), element_type="text", text="x", font_size=11)
        for y in range(3) for x in range(3)
    ]
    assert _is_grid(texts) is True


def test_is_grid_false():
    """Randomly placed texts should not be identified as a grid."""
    texts = [
        TextElement(bbox=Rect(x * 30, y * 50, 90, 14), element_type="text", text="x", font_size=11)
        for y, x in [(0, 0), (1, 3), (2, 1), (5, 8), (3, 2)]
    ]
    assert _is_grid(texts) is False
