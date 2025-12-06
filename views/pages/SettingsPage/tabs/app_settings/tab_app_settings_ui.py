from PySide6.QtCore import QRect, QSize, Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from components.utils import ColoredSpacer
from models.settings import settings_mapping

from ...field_registry import FieldRegistry


class TabAppSettingsUI(QWidget):
    secure_setting_change = Signal(str, str, str)

    def __init__(self, ui_helper):
        super().__init__()
        self.tab_id = "app_settings"
        self.settings_page_layout = QHBoxLayout(self)
        self.field_registery = FieldRegistry()

        self.uih = ui_helper

        self.inner_settings_page_layout = QHBoxLayout()
        self.settings_page_layout.addLayout(self.inner_settings_page_layout)
        self.vspacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.settings_page_layout.addItem(self.vspacer)

        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hspacer1 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.settings_page_layout.addItem(self.hspacer)

        # self.settings_page_layout.addItem(hspacer)
        self.settings_grid_layout = QGridLayout()
        self.settings_page_layout.addLayout(self.settings_grid_layout)

        self.columns = 4

        self.settings_page_layout.addItem(self.hspacer1)

        self.fields_to_map = settings_mapping[self.tab_id]

        for key, config in self.fields_to_map.items():
            self.uih.create_input_fields(
                self.tab_id, key, config, self.settings_grid_layout
            )

        self.vspacer2 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vspacer3 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.settings_grid_layout.addItem(
            self.vspacer2, self.settings_grid_layout.count() // self.columns, 2
        )
        self.google_auth_api_key_paste_btn = QPushButton("Paste API Key")
        self.vlayout_google_api_key = self.field_registery.get_field(
            f"{self.tab_id}/layout_{"google_api_key"}"
        )

        self.textEdit_google_api_key = self.field_registery.get_field(
            f"{self.tab_id}/text_edit_{"google_api_key"}"
        )

        self.vlayout_google_api_key.addWidget(self.google_auth_api_key_paste_btn)
        self.settings_page_layout.addItem(self.vspacer3)

        self.textEdit_google_api_key.setReadOnly(True)
        self.google_auth_api_key_paste_btn.clicked.connect(self.google_auth_paste_text)

    def google_auth_paste_text(self):
        """Handle pasting only."""
        print("here")
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        self.textEdit_google_api_key.setText(text)
        self.secure_setting_change.emit(self.tab_id, "google_api_key", text)
