import fitz
from src.core.model import (
    Document, Page, TextElement, ImageElement, TableRegion, Rect,
)
from src.core.reader import Reader


class PDFReader(Reader):
    @staticmethod
    def supported_extensions() -> list[str]:
        return [".pdf"]

    def read(self, filepath: str) -> Document:
        doc = fitz.open(filepath)
        metadata = dict(doc.metadata)
        pages = []

        for i, page in enumerate(doc):
            p = Page(page_number=i, width=page.rect.width, height=page.rect.height)
            self._extract_text_blocks(page, p)
            self._extract_images(page, p)
            self._extract_tables(page, p)
            pages.append(p)

        doc.close()
        return Document(pages=pages, metadata=metadata)

    def _extract_text_blocks(self, page: fitz.Page, p: Page) -> None:
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        for block in blocks:
            if block["type"] == 0:  # text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_flags = span.get("flags", 0)
                        te = TextElement(
                            bbox=Rect(
                                x=span["bbox"][0],
                                y=span["bbox"][1],
                                w=span["bbox"][2] - span["bbox"][0],
                                h=span["bbox"][3] - span["bbox"][1],
                            ),
                            element_type="text",
                            text=span["text"],
                            font_name=span.get("font", ""),
                            font_size=span.get("size", 0),
                            font_color=self._to_hex(span.get("color", 0)),
                            bold=bool(font_flags & 2**3),
                            italic=bool(font_flags & 2**0),
                        )
                        p.elements.append(te)

    def _extract_images(self, page: fitz.Page, p: Page) -> None:
        images = page.get_images(full=True)
        for img in images:
            xref = img[0]
            base_image = page.parent.extract_image(xref)
            rects = page.get_image_rects(img)
            bbox = rects[0] if rects else fitz.Rect(0, 0, 100, 100)
            ie = ImageElement(
                bbox=Rect(x=bbox.x0, y=bbox.y0, w=bbox.width, h=bbox.height),
                element_type="image",
                image_bytes=base_image["image"],
                image_format=base_image["ext"],
                width=base_image.get("width", 0),
                height=base_image.get("height", 0),
            )
            p.elements.append(ie)

    def _extract_tables(self, page: fitz.Page, p: Page) -> None:
        tabs = page.find_tables()
        for tab in tabs:
            rows = []
            for row in tab.extract():
                rows.append([str(cell) if cell else "" for cell in row])
            tr = TableRegion(
                bbox=Rect(
                    x=tab.bbox[0],
                    y=tab.bbox[1],
                    w=tab.bbox[2] - tab.bbox[0],
                    h=tab.bbox[3] - tab.bbox[1],
                ),
                element_type="table_region",
                rows=rows,
            )
            p.elements.append(tr)

    @staticmethod
    def _to_hex(color: int) -> str:
        if isinstance(color, int):
            return f"#{color & 0xFFFFFF:06x}"
        return "#000000"
