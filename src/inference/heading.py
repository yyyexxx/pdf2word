"""Detect headings from font size, weight, position, and numbering patterns."""

import re
import statistics
from src.core.model import Page, TextElement, SemanticHint


_NUMBERING = re.compile(
    r"^(第[一二三四五六七八九十\d]+[章节]|"
    r"Chapter\s+\d+|"
    r"\d+(\.\d+)*[\.\s]|"
    r"[IVX]+\.|"
    r"[一二三四五六七八九十]+[、．.]|"
    r"[（(][一二三四五六七八九十\d]+[)）])"
)


def detect_headings(pages: list[Page]) -> None:
    all_texts = _collect_texts(pages)
    if not all_texts:
        return

    font_sizes = [t.font_size for t in all_texts if t.font_size > 0]
    if not font_sizes:
        return

    median_size = statistics.median_low(font_sizes)
    page_height = pages[0].height if pages else 792

    for te in all_texts:
        text = te.text.strip()
        if not text:
            continue

        score = round(_heading_score(te, text, median_size, page_height), 2)
        if score >= 0.50:
            level = _heading_level(te.font_size, median_size, score)
            te.hint = SemanticHint(
                role="heading",
                level=level,
                confidence=min(0.98, score + 0.1),
            )


def _heading_score(te: TextElement, text: str, median_size: float, page_h: float) -> float:
    score = 0.0

    # 1. font size vs median
    ratio = te.font_size / median_size if median_size > 0 else 1
    if ratio >= 1.8:
        score += 0.40
    elif ratio >= 1.5:
        score += 0.30
    elif ratio >= 1.25:
        score += 0.15

    # 2. bold
    if te.bold:
        score += 0.15

    # 3. short text (< 60 chars) — headings are concise
    if len(text) < 30:
        score += 0.15
    elif len(text) < 60:
        score += 0.08

    # 4. numbering pattern
    if _NUMBERING.match(text):
        score += 0.20

    # 5. position: near top of page or after a large vertical gap
    page_top_ratio = te.bbox.y / page_h if page_h > 0 else 0
    if page_top_ratio < 0.15:
        score += 0.05

    return min(1.0, score)


def _heading_level(font_size: float, median_size: float, score: float) -> int:
    ratio = font_size / median_size if median_size > 0 else 1
    if ratio >= 1.8:
        return 1
    elif ratio >= 1.5:
        return 2
    elif ratio >= 1.25:
        return 3
    return 3 if score > 0.7 else 1


def _collect_texts(pages: list[Page]) -> list[TextElement]:
    result = []
    for page in pages:
        for e in page.elements:
            if isinstance(e, TextElement):
                result.append(e)
    return result
