from pathlib import Path
from PIL import Image as PILImage
from src.core.model import Document, Page, ImageElement, Rect
from src.core.reader import Reader


class ImageReader(Reader):
    @staticmethod
    def supported_extensions() -> list[str]:
        return [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"]

    def read(self, filepath: str) -> Document:
        img = PILImage.open(filepath)
        fmt = img.format.lower() if img.format else Path(filepath).suffix.lstrip(".")

        with open(filepath, "rb") as f:
            image_bytes = f.read()

        ie = ImageElement(
            bbox=Rect(x=0, y=0, w=img.width, h=img.height),
            element_type="image",
            image_bytes=image_bytes,
            image_format=fmt,
            width=img.width,
            height=img.height,
        )

        page = Page(
            page_number=0,
            width=img.width,
            height=img.height,
            elements=[ie],
        )

        return Document(pages=[page], metadata={"source": filepath, "format": fmt})
