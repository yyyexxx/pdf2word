import fitz
from src.core.model import Document, Page, ImageElement
from src.core.writer import Writer


class PDFWriter(Writer):
    @staticmethod
    def supported_extensions() -> list[str]:
        return [".pdf"]

    def write(self, doc: Document, output_path: str) -> None:
        out = fitz.open()

        for page in doc.pages:
            p = out.new_page(width=page.width, height=page.height)

            # insert images
            for element in page.elements:
                if isinstance(element, ImageElement):
                    rect = fitz.Rect(
                        element.bbox.x,
                        element.bbox.y,
                        element.bbox.x + element.bbox.w,
                        element.bbox.y + element.bbox.h,
                    )
                    p.insert_image(rect, stream=element.image_bytes)

        out.save(output_path)
        out.close()
