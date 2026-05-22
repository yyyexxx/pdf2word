from abc import ABC, abstractmethod
from src.core.model import Document


class Writer(ABC):
    @staticmethod
    @abstractmethod
    def supported_extensions() -> list[str]:
        ...

    @abstractmethod
    def write(self, doc: Document, output_path: str) -> None:
        ...
