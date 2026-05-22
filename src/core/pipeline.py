import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from src.core.model import Document
from src.core.reader import Reader
from src.core.writer import Writer
from src.core.readers.pdf_reader import PDFReader
from src.core.readers.image_reader import ImageReader
from src.core.writers.docx_writer import DocxWriter
from src.core.writers.pdf_writer import PDFWriter
from src.core.writers.image_writer import ImageWriter
from src.inference.infer import infer


READERS: dict[str, Reader] = {}
WRITERS: dict[str, Writer] = {}

# register readers
for cls in [PDFReader, ImageReader]:
    r = cls()
    for ext in cls.supported_extensions():
        READERS[ext] = r

# register writers
for cls in [DocxWriter, PDFWriter, ImageWriter]:
    w = cls()
    for ext in cls.supported_extensions():
        WRITERS[ext] = w

# when inference should run: formats where source is PDF and target needs structure
INFER_PAIRS = {(".pdf", ".docx")}


@dataclass
class ConversionResult:
    input_path: str
    output_path: str
    success: bool
    error: str = ""


@dataclass
class BatchResult:
    results: list[ConversionResult] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if not r.success)


class Pipeline:
    def __init__(
        self,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ):
        self.progress_callback = progress_callback

    def _report(self, current: int, total: int, message: str) -> None:
        if self.progress_callback:
            self.progress_callback(current, total, message)

    def convert(
        self,
        files: list[str],
        target_ext: str,
        output_dir: str | None = None,
    ) -> BatchResult:
        target_ext = target_ext.lower()
        if target_ext not in WRITERS:
            raise ValueError(f"Unsupported target format: {target_ext}")

        writer = WRITERS[target_ext]
        batch = BatchResult()
        total = len(files)

        for idx, filepath in enumerate(files):
            self._report(idx, total, f"处理中: {Path(filepath).name}")

            try:
                src_ext = Path(filepath).suffix.lower()
                if src_ext not in READERS:
                    batch.results.append(ConversionResult(
                        filepath, "", False,
                        f"不支持的源格式: {src_ext}",
                    ))
                    continue

                reader = READERS[src_ext]
                doc = reader.read(filepath)

                # run inference if needed
                if (src_ext, target_ext) in INFER_PAIRS:
                    doc = infer(doc)

                out_path = self._output_path(filepath, target_ext, output_dir)
                writer.write(doc, out_path)

                batch.results.append(ConversionResult(filepath, out_path, True))

            except Exception:
                batch.results.append(ConversionResult(
                    filepath, "", False,
                    traceback.format_exc(),
                ))

        self._report(total, total, "转换完成")
        return batch

    @staticmethod
    def _output_path(input_path: str, target_ext: str, output_dir: str | None) -> str:
        stem = Path(input_path).stem
        parent = output_dir or str(Path(input_path).parent)
        return str(Path(parent) / f"{stem}{target_ext}")

    @staticmethod
    def detect_format(filepath: str) -> str:
        ext = Path(filepath).suffix.lower()
        return ext

    @staticmethod
    def available_targets(source_ext: str) -> list[str]:
        """Return list of target extensions this source can convert to."""
        source_ext = source_ext.lower()
        targets = []
        for ext, writer in WRITERS.items():
            # skip self-conversion
            if ext == source_ext:
                continue
            targets.append(ext)
        return sorted(targets)
