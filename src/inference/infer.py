from src.core.model import Document
from src.inference.paragraph import merge_paragraphs
from src.inference.heading import detect_headings
from src.inference.table import detect_tables


def infer(doc: Document) -> Document:
    pages = doc.pages
    detect_tables(pages)
    detect_headings(pages)   # first: tag headings so merge can skip them
    merge_paragraphs(pages)  # then: merge remaining body text
    return doc
