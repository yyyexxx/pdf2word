from PySide6.QtWidgets import QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
from PySide6.QtCore import Qt


class DropZone(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.file_list = QListWidget()

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("选择文件")
        add_btn.clicked.connect(self._add_files)

        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self._clear_files)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()

        layout.addWidget(self.file_list)
        layout.addLayout(btn_layout)

        self.setStyleSheet(self._style())

    def _style(self) -> str:
        return """
            DropZone {
                border: 2px dashed #aaa;
                border-radius: 8px;
                background: #fafafa;
                min-height: 150px;
            }
            QListWidget {
                border: none;
                background: transparent;
            }
        """

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        self.file_list.addItems(paths)
        event.acceptProposedAction()

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择文件",
            "",
            "支持的文件 (*.pdf *.png *.jpg *.jpeg *.bmp *.tiff *.tif);;PDF (*.pdf);;图片 (*.png *.jpg *.jpeg *.bmp *.tiff)",
        )
        if files:
            self.file_list.addItems(files)

    def _clear_files(self):
        self.file_list.clear()

    def get_files(self) -> list[str]:
        return [self.file_list.item(i).text() for i in range(self.file_list.count())]

    @property
    def has_files(self) -> bool:
        return self.file_list.count() > 0
