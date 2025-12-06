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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from components.utils import ColoredSpacer

from .field_registry import FieldRegistry


class PageSettingsUI(QWidget):
    folder_submit = Signal(str, str)
    secure_setting_change = Signal(str, str)

    def __init__(self, ui_helper):
        super().__init__()
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
        self.uih.create_input_fields(
            "apple_note_name",
            "Apple Note Name:",
            "Verify Apple Note",
            self.settings_grid_layout,
        )
        self.uih.create_input_fields(
            "anki_words_deck_name",
            "Word's Deck Name:",
            "Verify Deck",
            self.settings_grid_layout,
        )
        self.uih.create_input_fields(
            "anki_sents_deck_name",
            "Sents's Deck Name:",
            "Verify Deck",
            self.settings_grid_layout,
        )

        self.uih.create_input_fields(
            "anki_words_model_name",
            "Word's Model Name:",
            "Verify Model",
            self.settings_grid_layout,
        )
        self.uih.create_input_fields(
            "anki_sents_model_name",
            "Sent's Model Name:",
            "Verify Model",
            self.settings_grid_layout,
        )

        self.uih.create_input_fields(
            "anki_user", "Anki User Name:", "Verify User", self.settings_grid_layout
        )
        self.uih.create_input_fields(
            "anki_audio_path",
            "Anki Audio path:",
            "Verify Audio Path",
            self.settings_grid_layout,
            folder_icon=True,
        )
        self.uih.create_input_fields(
            "log_file_path",
            "Log File path:",
            "Verify Log Path",
            self.settings_grid_layout,
            folder_icon=True,
        )
        self.uih.create_input_fields(
            "log_file_name",
            "Log File Name:",
            "Save Log File Name",
            self.settings_grid_layout,
        )
        self.uih.create_input_fields(
            "log_backup_count",
            "Log Backup Count:",
            "Save Log Backup Count",
            self.settings_grid_layout,
            field_type="int",
        )

        self.uih.create_input_fields(
            "log_file_max_mbs",
            "Log File Max Mbs:",
            "Save Log File Max Mbs",
            self.settings_grid_layout,
            field_type="int",
        )

        self.uih.create_input_fields(
            "log_keep_files_days",
            "Keep Log File Days:",
            "Save Log File Days",
            self.settings_grid_layout,
            field_type="int",
        )

        self.uih.create_input_fields(
            "dictionary_source",
            "Dictionary Source:",
            "Save Dictionary Source",
            self.settings_grid_layout,
            lineEdit=False,
            comboBox=["cpod", "mgdb"],
        )

        self.uih.create_input_fields(
            "auto_save_on_close",
            "Auto Save on Close:",
            "Save Auto Close",
            self.settings_grid_layout,
            lineEdit=False,
            comboBox=["True", "False"],
        )

        (
            self.textEdit_google_api_key,
            self.label_google_api_key_verified_icon,
            self.btn_google_api_key_verify,
            self.vlayout_google_api_key,
        ) = self.uih.create_input_fields(
            "google_api_key",
            "Google Service:",
            "Verify Google Service",
            self.settings_grid_layout,
            False,
        )
        self.vspacer2 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vspacer3 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.settings_grid_layout.addItem(
            self.vspacer2, self.settings_grid_layout.count() // self.columns, 2
        )
        self.google_auth_api_key_paste_btn = QPushButton("Paste API Key")
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
        self.secure_setting_change.emit("google_api_key", text)
