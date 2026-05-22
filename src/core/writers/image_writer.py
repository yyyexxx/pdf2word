import io
from pathlib import Path
from PIL import Image as PILImage
from src.core.model import Document, ImageElement
from src.core.writer import Writer


class ImageWriter(Writer):
    @staticmethod
    def supported_extensions() -> list[str]:
        return [".png", ".jpg", ".jpeg"]

    def write(self, doc: Document, output_path: str) -> None:
        ext = Path(output_path).suffix.lower()
        fmt = "PNG" if ext == ".png" else "JPEG"

        if len(doc.pages) == 1:
            self._write_single(doc.pages[0], output_path, fmt)
        else:
            # multi-page: write each page as separate file
            base = Path(output_path)
            stem = base.stem
            parent = base.parent
            for page in doc.pages:
                out = parent / f"{stem}_page{page.page_number + 1}{ext}"
                self._write_single(page, str(out), fmt, page_number=page.page_number)

    def _write_single(self, page, output_path: str, fmt: str, page_number: int = 0) -> None:
        for element in page.elements:
            if isinstance(element, ImageElement):
                img = PILImage.open(io.BytesIO(element.image_bytes))
                rgb = img.convert("RGB") if fmt == "JPEG" else img
                rgb.save(output_path, format=fmt)
                return

        # no image found: create blank image
        w = int(page.width) or 800
        h = int(page.height) or 600
        blank = PILImage.new("RGB", (w, h), (255, 255, 255))
        blank.save(output_path, format=fmt)
