from PySide6.QtCore import QThread, Signal
from src.core.pipeline import Pipeline, BatchResult


class ConvertThread(QThread):
    progress = Signal(int, int, str)  # current, total, message
    finished = Signal(object)         # BatchResult

    def __init__(self, files: list[str], target_ext: str, output_dir: str = None):
        super().__init__()
        self.files = files
        self.target_ext = target_ext
        self.output_dir = output_dir

    def run(self):
        pipeline = Pipeline(progress_callback=self._on_progress)
        result = pipeline.convert(self.files, self.target_ext, self.output_dir)
        self.finished.emit(result)

    def _on_progress(self, current: int, total: int, message: str):
        self.progress.emit(current, total, message)
