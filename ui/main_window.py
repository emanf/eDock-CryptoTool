from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.ui.base_ui import eD_UIBase

from ..services.transform_service import TransformService


class CryptoToolWindow(QMainWindow, eD_UIBase):
    def __init__(self, app_ref=None, parent=None):
        super().__init__(parent)
        self._init_ui_base(app=app_ref, context=getattr(app_ref, "context", None))

        self.setWindowTitle("Crypto Tool")
        self.resize(820, 680)
        self.setMinimumSize(720, 560)

        self.transform_service = TransformService()
        self._mode = "encrypt"
        self._result_rows = {}
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(80)
        self._refresh_timer.timeout.connect(self._refresh_outputs)

        self._build_ui()
        self._apply_mode("encrypt")

    def show_and_activate(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("cryptoRoot")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        title_box = QWidget()
        title_layout = QVBoxLayout(title_box)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        title = QLabel("Crypto Tool")
        title.setObjectName("titleLabel")
        title_layout.addWidget(title)

        subtitle = QLabel("Type once and every transform updates instantly")
        subtitle.setObjectName("subtitleLabel")
        title_layout.addWidget(subtitle)

        header_layout.addWidget(title_box, 1)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Encrypt", "Decrypt"])
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        self.mode_combo.setFixedWidth(128)
        self.mode_combo.setObjectName("modeCombo")
        header_layout.addWidget(self.mode_combo)

        self.paste_btn = QPushButton("Paste")
        self.paste_btn.clicked.connect(self._paste_clipboard)
        self.paste_btn.setFixedWidth(76)
        self.paste_btn.setCursor(Qt.PointingHandCursor)
        self.paste_btn.setObjectName("pasteButton")
        header_layout.addWidget(self.paste_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_input)
        self.clear_btn.setFixedWidth(76)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setObjectName("clearButton")
        header_layout.addWidget(self.clear_btn)

        root.addWidget(header)

        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("Enter text to transform")
        self.input_edit.setMinimumHeight(120)
        self.input_edit.setMaximumHeight(160)
        self.input_edit.setObjectName("inputEdit")
        self.input_edit.textChanged.connect(self._on_input_changed)
        root.addWidget(self.input_edit)

        output_header = QWidget()
        output_header_layout = QHBoxLayout(output_header)
        output_header_layout.setContentsMargins(0, 0, 0, 0)
        output_header_layout.setSpacing(8)

        output_title = QLabel("Outputs")
        output_title.setObjectName("sectionLabel")
        output_header_layout.addWidget(output_title)

        output_header_layout.addStretch()

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        output_header_layout.addWidget(self.status_label)

        root.addWidget(output_header)

        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setFrameShape(QScrollArea.NoFrame)
        self.results_scroll.setObjectName("resultsScroll")

        self.results_container = QWidget()
        self.results_container.setObjectName("resultsContainer")

        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(6)

        self.results_scroll.setWidget(self.results_container)
        root.addWidget(self.results_scroll, 1)

        self.setStyleSheet(
            """
            QWidget#cryptoRoot {
                background-color: #f3f4f6;
            }
            QLabel#titleLabel {
                color: #111827;
                font-size: 20px;
                font-weight: 800;
            }
            QLabel#subtitleLabel {
                color: #6b7280;
                font-size: 12px;
            }
            QLabel#sectionLabel {
                color: #111827;
                font-size: 13px;
                font-weight: 700;
            }
            QLabel#statusLabel {
                color: #6b7280;
                font-size: 12px;
            }
            QComboBox#modeCombo {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 7px 34px 7px 10px;
                font-weight: 700;
            }
            QComboBox#modeCombo:hover {
                border-color: #a5b4fc;
                background-color: #f9fafb;
            }
            QComboBox#modeCombo:focus {
                border-color: #6366f1;
            }
            QComboBox#modeCombo::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border-left: 1px solid #e5e7eb;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background-color: #f9fafb;
            }
            QComboBox#modeCombo::drop-down:hover {
                background-color: #eef2ff;
            }
            QComboBox#modeCombo::down-arrow {
                image: url(apps/emanf.crypto_tool/assets/chevron_down.svg);
                border: none;
                width: 12px;
                height: 12px;
            }
            QComboBox#modeCombo QAbstractItemView {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 4px;
                selection-background-color: #eef2ff;
                selection-color: #3730a3;
                outline: none;
            }
            QPushButton#pasteButton {
                background-color: #eef2ff;
                color: #3730a3;
                border: 1px solid #c7d2fe;
                border-radius: 8px;
                padding: 7px 10px;
                font-weight: 700;
            }
            QPushButton#pasteButton:hover {
                background-color: #e0e7ff;
            }
            QPushButton#clearButton {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 7px 10px;
                font-weight: 600;
            }
            QPushButton#clearButton:hover {
                background-color: #f9fafb;
            }
            QTextEdit#inputEdit {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 9px;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
                font-family: Consolas, "Courier New", monospace;
                font-size: 13px;
            }
            QScrollArea#resultsScroll {
                background: transparent;
                border: none;
            }
            QWidget#resultsContainer {
                background: transparent;
            }
            QFrame[resultRow="true"] {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
            QLabel[resultName="true"] {
                color: #111827;
                font-weight: 700;
                font-size: 12px;
            }
            QLineEdit[resultValue="true"] {
                background-color: #f9fafb;
                color: #1f2937;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 7px 9px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 12px;
            }
            QLineEdit[resultValueError="true"] {
                background-color: #fff5f5;
                color: #c0392b;
                border: 1px solid #f2c2c2;
                border-radius: 8px;
                padding: 7px 9px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 12px;
            }
            QPushButton[copyButton="true"] {
                background-color: #eef2ff;
                color: #3730a3;
                border: 1px solid #c7d2fe;
                border-radius: 8px;
                padding: 6px 10px;
                font-weight: 700;
            }
            QPushButton[copyButton="true"]:hover {
                background-color: #e0e7ff;
            }
            QPushButton[copyButton="true"]:disabled {
                background-color: #f3f4f6;
                color: #9ca3af;
                border: 1px solid #e5e7eb;
            }
            """
        )

        self._refresh_outputs()

    def _paste_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        self.input_edit.setPlainText(clipboard.text())

    def _clear_input(self):
        self.input_edit.clear()

    def _on_input_changed(self):
        self._refresh_timer.start()

    def _on_mode_changed(self, text):
        self._apply_mode(text.lower())

    def _apply_mode(self, mode):
        self._mode = "encrypt" if mode != "decrypt" else "decrypt"
        self._refresh_outputs()

    def _refresh_outputs(self):
        text = self.input_edit.toPlainText()
        items = self.transform_service.transform(text, self._mode)

        for item in items:
            name = item.get("name", "")
            if name not in self._result_rows:
                self._create_result_row(item)
            self._update_result_row(item)

        active_names = {item.get("name", "") for item in items}
        for name in list(self._result_rows.keys()):
            if name not in active_names:
                row = self._result_rows.pop(name)
                row["widget"].deleteLater()

        self.results_layout.addStretch(1)
        while self.results_layout.count() > len(self._result_rows) + 1:
            layout_item = self.results_layout.takeAt(self.results_layout.count() - 2)
            if layout_item is not None and layout_item.spacerItem() is not None:
                continue

        self.status_label.setText(f"{len(items)} transforms · {self._mode}")

    def _create_result_row(self, item):
        name = item.get("name", "")

        row = QFrame()
        row.setProperty("resultRow", True)
        row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 8, 10, 8)
        row_layout.setSpacing(8)

        name_label = QLabel(name)
        name_label.setProperty("resultName", True)
        name_label.setFixedWidth(120)
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row_layout.addWidget(name_label)

        value_edit = QLineEdit()
        value_edit.setReadOnly(True)
        value_edit.setProperty("resultValue", True)
        value_edit.setMinimumHeight(34)
        value_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        value_edit.setCursorPosition(0)
        row_layout.addWidget(value_edit, 1)

        copy_button = QPushButton("Copy")
        copy_button.setProperty("copyButton", True)
        copy_button.setFixedWidth(72)
        copy_button.setMinimumHeight(34)
        copy_button.setCursor(Qt.PointingHandCursor)
        copy_button.clicked.connect(lambda checked=False, transform_name=name: self._copy_value(transform_name))
        row_layout.addWidget(copy_button, 0)

        self.results_layout.insertWidget(self.results_layout.count(), row)

        self._result_rows[name] = {
            "widget": row,
            "name": name_label,
            "value": value_edit,
            "copy": copy_button,
            "payload": item,
        }

    def _update_result_row(self, item):
        name = item.get("name", "")
        row = self._result_rows.get(name)
        if row is None:
            return

        value = item.get("value") if item.get("value") is not None else ""
        error = item.get("error") or ""
        shown_value = error if error else value
        copyable = bool(item.get("copyable", True)) and bool(shown_value) and not bool(error)

        value_edit = row["value"]
        copy_button = row["copy"]

        if value_edit.text() != shown_value:
            cursor_position = value_edit.cursorPosition()
            value_edit.setText(shown_value)
            value_edit.setCursorPosition(min(cursor_position, len(shown_value)))

        value_edit.setProperty("resultValue", not bool(error))
        value_edit.setProperty("resultValueError", bool(error))
        value_edit.style().unpolish(value_edit)
        value_edit.style().polish(value_edit)

        copy_button.setEnabled(copyable)
        copy_button.setText("Copy")

        row["payload"] = item

    def _copy_value(self, name):
        row = self._result_rows.get(name)
        if row is None:
            return

        item = row.get("payload") or {}
        value = item.get("value") or ""
        if item.get("error"):
            return

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(value)

        button = row["copy"]
        button.setText("Copied")
        QTimer.singleShot(1200, lambda: self._reset_copy_button(button))

    def _reset_copy_button(self, button):
        if button is None:
            return
        button.setText("Copy")
