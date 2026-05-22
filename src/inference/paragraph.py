"""Merge nearby TextElements into paragraphs with column-aware reading order."""

from src.core.model import Page, TextElement, SemanticHint


_COLUMN_GAP_MIN = 20  # minimum horizontal whitespace to consider a column boundary (pt)


def merge_paragraphs(pages: list[Page]) -> None:
    for page in pages:
        texts = [e for e in page.elements if isinstance(e, TextElement)]
        if len(texts) < 2:
            continue

        columns = _detect_columns(texts)
        if not columns:
            _merge_in_line_order(texts, page)
        else:
            for col_x_min, col_x_max in columns:
                col_texts = [
                    t for t in texts
                    if t.bbox.x >= col_x_min - 5 and t.bbox.x + t.bbox.w <= col_x_max + 5
                ]
                col_texts.sort(key=lambda t: t.bbox.y)
                _merge_in_line_order(col_texts, page)


def _detect_columns(texts: list[TextElement]) -> list[tuple[float, float]]:
    """Find columns by detecting vertical gaps in x-coordinate histogram.

    Returns list of (x_min, x_max) tuples, or empty list if single column.
    """
    if len(texts) < 4:
        return []

    x_centers = sorted(t.bbox.x + t.bbox.w / 2 for t in texts)
    gaps = []
    for i in range(1, len(x_centers)):
        gap = x_centers[i] - x_centers[i - 1]
        if gap > _COLUMN_GAP_MIN:
            gaps.append((x_centers[i - 1], x_centers[i]))

    if not gaps:
        return []

    # find the largest gap as the column boundary
    max_gap = max(gaps, key=lambda g: g[1] - g[0])
    boundary = (max_gap[0] + max_gap[1]) / 2

    x_min = min(t.bbox.x for t in texts)
    x_max = max(t.bbox.x + t.bbox.w for t in texts)

    return [(x_min, boundary), (boundary, x_max)]


def _merge_in_line_order(texts: list[TextElement], page: Page) -> None:
    """Merge elements that belong to the same paragraph, top-to-bottom."""
    if len(texts) < 2:
        return

    i = 0
    while i < len(texts):
        current = texts[i]

        if current.hint and current.hint.role == "heading":
            i += 1
            continue

        current_text = current.text
        right_edge = current.bbox.x + current.bbox.w
        bottom = current.bbox.y + current.bbox.h
        center_y = current.bbox.y + current.bbox.h / 2

        j = i + 1
        while j < len(texts):
            nxt = texts[j]
            if nxt.hint and nxt.hint.role == "heading":
                j += 1
                continue

            nxt_center_y = nxt.bbox.y + nxt.bbox.h / 2
            x_gap = nxt.bbox.x - right_edge
            y_center_diff = abs(nxt_center_y - center_y)
            y_gap = nxt.bbox.y - bottom

            same_line = y_center_diff < current.bbox.h * 0.8 and 0 <= x_gap < current.bbox.h * 3
            next_line = 0 < y_gap < current.bbox.h * 2.5 and abs(nxt.bbox.x - current.bbox.x) < current.bbox.w * 0.3

            if same_line or next_line:
                sep = " " if same_line else "\n"
                current_text += sep + nxt.text
                right_edge = max(right_edge, nxt.bbox.x + nxt.bbox.w)
                bottom = nxt.bbox.y + nxt.bbox.h
                center_y = (current.bbox.y + bottom) / 2
                page.elements.remove(nxt)
                texts.remove(nxt)
            else:
                break

        if current_text != current.text:
            current.text = current_text
            current.bbox.w = right_edge - current.bbox.x
            current.bbox.h = bottom - current.bbox.y
            if current.hint is None:
                current.hint = SemanticHint(role="paragraph", confidence=0.8)
        i += 1
