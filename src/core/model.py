from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float


@dataclass
class SemanticHint:
    role: str       # "heading" | "paragraph" | "list_item" | "table_cell"
    level: int = 0  # 1-6 for heading, 0 for others
    confidence: float = 1.0


@dataclass
class PageElement:
    bbox: Rect
    element_type: str  # "text" | "image" | "table_region"


@dataclass
class TextElement(PageElement):
    text: str = ""
    font_name: str = ""
    font_size: float = 0
    font_color: str = "#000000"
    bold: bool = False
    italic: bool = False
    hint: Optional[SemanticHint] = None


@dataclass
class ImageElement(PageElement):
    image_bytes: bytes = b""
    image_format: str = "png"
    width: float = 0
    height: float = 0


@dataclass
class TableRegion(PageElement):
    rows: list[list[str]] = field(default_factory=list)


@dataclass
class Page:
    page_number: int
    width: float
    height: float
    elements: list[PageElement] = field(default_factory=list)


@dataclass
class Document:
    pages: list[Page] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
