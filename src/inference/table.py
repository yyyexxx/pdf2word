"""Detect borderless tables from text alignment patterns.

When PyMuPDF's find_tables() misses a table (no visible borders),
this module detects grid-aligned text and groups it into TableRegions."""

from collections import defaultdict
from src.core.model import Page, TextElement, TableRegion, Rect


_X_CLUSTER_TOLERANCE = 10  # pt — x coords within this are the same column
_Y_CLUSTER_TOLERANCE = 8   # pt — y coords within this are the same row
_MIN_ROWS = 2
_MIN_COLS = 2
_MIN_CELLS_FOR_TABLE = 4  # at least 4 cells to consider it a table


def detect_tables(pages: list[Page]) -> None:
    """Detect borderless tables on each page by analyzing text alignment."""
    for page in pages:
        texts = [e for e in page.elements if isinstance(e, TextElement)]
        if len(texts) < _MIN_CELLS_FOR_TABLE:
            continue

        # find text clusters that form a grid
        regions = _find_grid_regions(texts)
        for region in regions:
            table = _build_table_region(region)
            if table:
                # remove original text elements and add table region
                for te in region:
                    if te in page.elements:
                        page.elements.remove(te)
                page.elements.append(table)


def _find_grid_regions(texts: list[TextElement]) -> list[list[TextElement]]:
    """Group texts by spatial proximity and return those forming grids."""
    # simple approach: cluster all texts on the page, check if they form a grid
    candidates = [t for t in texts if not t.hint or t.hint.role != "heading"]
    if len(candidates) < _MIN_CELLS_FOR_TABLE:
        return []

    # cluster by y proximity to separate table rows from surrounding paragraphs
    y_sorted = sorted(candidates, key=lambda t: t.bbox.y)
    groups = []
    current_group = [y_sorted[0]]

    for i in range(1, len(y_sorted)):
        prev = y_sorted[i - 1]
        curr = y_sorted[i]
        gap = curr.bbox.y - (prev.bbox.y + prev.bbox.h)
        avg_h = (prev.bbox.h + curr.bbox.h) / 2

        if gap < avg_h * 2:
            current_group.append(curr)
        else:
            groups.append(current_group)
            current_group = [curr]

    groups.append(current_group)

    # check each group for grid structure
    result = []
    for group in groups:
        if _is_grid(group):
            result.append(group)

    return result


def _is_grid(texts: list[TextElement]) -> bool:
    """Check if a set of text elements forms a grid (consistent columns across rows)."""
    if len(texts) < _MIN_CELLS_FOR_TABLE:
        return False

    x_coords = sorted(t.bbox.x for t in texts)
    cols = _cluster_1d(x_coords, _X_CLUSTER_TOLERANCE)
    y_coords = sorted(t.bbox.y for t in texts)
    rows = _cluster_1d(y_coords, _Y_CLUSTER_TOLERANCE)

    if len(cols) < _MIN_COLS or len(rows) < _MIN_ROWS:
        return False

    # check fill rate: at least 50% of grid cells populated
    total_cells = len(cols) * len(rows)
    filled = 0
    for t in texts:
        col_idx = _nearest_cluster(t.bbox.x, cols, _X_CLUSTER_TOLERANCE)
        row_idx = _nearest_cluster(t.bbox.y, rows, _Y_CLUSTER_TOLERANCE)
        if col_idx is not None and row_idx is not None:
            filled += 1

    return filled / total_cells >= 0.5


def _cluster_1d(values: list[float], tolerance: float) -> list[float]:
    """Cluster 1D coordinates into representative positions."""
    if not values:
        return []
    values = sorted(values)
    clusters = [values[0]]
    for v in values[1:]:
        if v - clusters[-1] > tolerance:
            clusters.append(v)
    return clusters


def _nearest_cluster(value: float, clusters: list[float], tolerance: float = _X_CLUSTER_TOLERANCE) -> int | None:
    """Find nearest cluster index within tolerance."""
    for i, c in enumerate(clusters):
        if abs(value - c) < tolerance * 2:
            return i
    return None


def _build_table_region(texts: list[TextElement]) -> TableRegion | None:
    """Build a TableRegion from grid-aligned texts."""
    x_coords = sorted(set(t.bbox.x for t in texts))
    cols = _cluster_1d(x_coords, _X_CLUSTER_TOLERANCE)
    y_coords = sorted(set(t.bbox.y for t in texts))
    rows = _cluster_1d(y_coords, _Y_CLUSTER_TOLERANCE)

    # build a dict of (row, col) -> text
    grid: dict[tuple[int, int], str] = defaultdict(str)
    for t in texts:
        col = _nearest_cluster(t.bbox.x, cols, _X_CLUSTER_TOLERANCE)
        row = _nearest_cluster(t.bbox.y, rows, _Y_CLUSTER_TOLERANCE)
        if col is not None and row is not None:
            existing = grid[(row, col)]
            grid[(row, col)] = (existing + " " + t.text).strip()

    sorted_rows = sorted(set(r for r, _ in grid))
    sorted_cols = sorted(set(c for _, c in grid))

    result_rows = []
    for r in sorted_rows:
        row = [grid.get((r, c), "") for c in sorted_cols]
        result_rows.append(row)

    if not result_rows:
        return None

    # compute bounding box
    x_min = min(t.bbox.x for t in texts)
    y_min = min(t.bbox.y for t in texts)
    x_max = max(t.bbox.x + t.bbox.w for t in texts)
    y_max = max(t.bbox.y + t.bbox.h for t in texts)

    return TableRegion(
        bbox=Rect(x=x_min, y=y_min, w=x_max - x_min, h=y_max - y_min),
        element_type="table_region",
        rows=result_rows,
    )
