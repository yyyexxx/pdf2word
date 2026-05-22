import os
import tempfile
from PIL import Image as PILImage
from src.core.readers.image_reader import ImageReader
from src.core.model import ImageElement


def test_image_reader_png():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        tmp = f.name
    try:
        img = PILImage.new("RGB", (100, 50), (255, 0, 0))
        img.save(tmp, format="PNG")

        reader = ImageReader()
        doc = reader.read(tmp)
        assert len(doc.pages) == 1
        page = doc.pages[0]
        assert page.width == 100
        assert page.height == 50
        assert len(page.elements) == 1
        ie = page.elements[0]
        assert isinstance(ie, ImageElement)
        assert ie.image_format == "png"
        assert len(ie.image_bytes) > 0
    finally:
        os.unlink(tmp)


def test_image_reader_supported_extensions():
    exts = ImageReader.supported_extensions()
    assert ".png" in exts
    assert ".jpg" in exts
