from abc import ABC, abstractmethod
from src.core.model import Document


class Reader(ABC):
    @staticmethod
    @abstractmethod
    def supported_extensions() -> list[str]:
        ...

    @abstractmethod
    def read(self, filepath: str) -> Document:
        ...
