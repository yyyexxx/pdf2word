from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QProgressBar, QMessageBox, QFileDialog,
)
from PySide6.QtCore import Qt
from src.ui.drop_zone import DropZone
from src.ui.convert_thread import ConvertThread
from src.core.pipeline import Pipeline, BatchResult


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文档格式转换器")
        self.setMinimumSize(560, 480)
        self._thread: ConvertThread | None = None
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Section 1: drop zone
        layout.addWidget(QLabel("文件列表"))
        self.drop_zone = DropZone()
        self.drop_zone.file_list.model().rowsInserted.connect(self._on_files_changed)
        self.drop_zone.file_list.model().rowsRemoved.connect(self._on_files_changed)
        layout.addWidget(self.drop_zone, stretch=1)

        # Section 2: format selection
        fmt_layout = QHBoxLayout()
        fmt_layout.setSpacing(16)

        fmt_layout.addWidget(QLabel("源格式:"))
        self.src_label = QLabel("—")
        self.src_label.setStyleSheet("font-weight: bold;")
        fmt_layout.addWidget(self.src_label)

        fmt_layout.addStretch()

        fmt_layout.addWidget(QLabel("转换为:"))
        self.target_combo = QComboBox()
        self.target_combo.setMinimumWidth(120)
        self.target_combo.setEnabled(False)
        fmt_layout.addWidget(self.target_combo)

        layout.addLayout(fmt_layout)

        # Section 3: convert button + progress
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.setMinimumHeight(40)
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._on_convert)
        layout.addWidget(self.convert_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def _on_files_changed(self):
        files = self.drop_zone.get_files()
        if not files:
            self.src_label.setText("—")
            self.target_combo.clear()
            self.target_combo.setEnabled(False)
            self.convert_btn.setEnabled(False)
            return

        # detect format from first file
        ext = Pipeline.detect_format(files[0])
        self.src_label.setText(ext)

        targets = Pipeline.available_targets(ext)
        self.target_combo.clear()
        self.target_combo.addItems(targets)
        self.target_combo.setEnabled(True)

        self.convert_btn.setEnabled(True)

    def _on_convert(self):
        files = self.drop_zone.get_files()
        if not files:
            return

        target_ext = self.target_combo.currentText()
        if not target_ext:
            return

        output_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if not output_dir:
            return

        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(files))
        self.progress_bar.setValue(0)
        self.status_label.setText("转换中...")

        self._thread = ConvertThread(files, target_ext, output_dir)
        self._thread.progress.connect(self._on_progress)
        self._thread.finished.connect(self._on_finished)
        self._thread.start()

    def _on_progress(self, current: int, total: int, message: str):
        self.progress_bar.setValue(current)
        self.status_label.setText(message)

    def _on_finished(self, result: BatchResult):
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        msg = f"转换完成: {result.success_count} 成功, {result.fail_count} 失败"

        if result.fail_count > 0:
            detail = "\n".join(
                f"{Path(r.input_path).name}: {r.error[:200]}"
                for r in result.results if not r.success
            )
            QMessageBox.warning(self, "转换结果", f"{msg}\n\n失败详情:\n{detail}")
        else:
            QMessageBox.information(self, "转换结果", msg)

        self.status_label.setText(msg)
