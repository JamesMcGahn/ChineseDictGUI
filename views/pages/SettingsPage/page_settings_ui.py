from PySide6.QtCore import QRect, QSize, Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
)

from base import QSingleton, QWidgetBase
from components.utils import ColoredSpacer
from models.settings import AppSettingsModel

from .field_registry import FieldRegistry
from .settings_ui_helper import SettingsUIHelper


class PageSettingsUI(QWidgetBase, metaclass=QSingleton):
    folder_submit = Signal(str, str)
    secure_setting_change = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.settings_page_layout = QHBoxLayout(self)
        self.field_registery = FieldRegistry()
        self.app_settings = AppSettingsModel()
        self.uih = SettingsUIHelper()
        self.app_settings.get_settings()
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
        (
            self.lineEdit_apple_note_name,
            self.label_apple_note_name_verified_icon,
            self.btn_apple_note_name_verify,
            self.hlayout_apple_note_name,
        ) = self.uih.create_input_fields(
            "apple_note_name",
            "Apple Note Name:",
            "Verify Apple Note",
            self.settings_grid_layout,
        )
        (
            self.lineEdit_anki_words_deck_name,
            self.label_anki_words_deck_name_verified_icon,
            self.btn_anki_words_deck_name_verify,
            self.hlayout_anki_words_deck_name,
        ) = self.uih.create_input_fields(
            "anki_words_deck_name",
            "Word's Deck Name:",
            "Verify Deck",
            self.settings_grid_layout,
        )
        (
            self.lineEdit_anki_sents_deck_name,
            self.label_anki_sents_deck_name_verified_icon,
            self.btn_anki_sents_deck_name_verify,
            self.hlayout_sents_anki_deck_name,
        ) = self.uih.create_input_fields(
            "anki_sents_deck_name",
            "Sents's Deck Name:",
            "Verify Deck",
            self.settings_grid_layout,
        )

        (
            self.lineEdit_anki_words_model_name,
            self.label_anki_words_model_name_verified_icon,
            self.btn_anki_words_model_name_verify,
            self.hlayout_anki_words_model_name,
        ) = self.uih.create_input_fields(
            "anki_words_model_name",
            "Word's Model Name:",
            "Verify Model",
            self.settings_grid_layout,
        )
        (
            self.lineEdit_anki_sents_model_name,
            self.label_anki_sents_model_name_verified_icon,
            self.btn_anki_sents_model_name_verify,
            self.hlayout_anki_sents_model_name,
        ) = self.uih.create_input_fields(
            "anki_sents_model_name",
            "Sent's Model Name:",
            "Verify Model",
            self.settings_grid_layout,
        )

        (
            self.lineEdit_anki_user,
            self.label_anki_user_verified_icon,
            self.btn_anki_user_verify,
            self.hlayout_anki_user,
        ) = self.uih.create_input_fields(
            "anki_user", "Anki User Name:", "Verify User", self.settings_grid_layout
        )
        (
            self.lineEdit_anki_audio_path,
            self.label_anki_audio_path_verified_icon,
            self.btn_anki_audio_path_verify,
            self.hlayout_anki_audio_path,
            self.btn_anki_audio_path_folder,
        ) = self.uih.create_input_fields(
            "anki_audio_path",
            "Anki Audio path:",
            "Verify Audio Path",
            self.settings_grid_layout,
            folder_icon=True,
        )
        (
            self.lineEdit_log_file_path,
            self.label_log_file_path_verified_icon,
            self.btn_log_file_path_verify,
            self.hlayout_log_file_path,
            self.btn_log_file_path_folder,
        ) = self.uih.create_input_fields(
            "log_file_path",
            "Log File path:",
            "Verify Log Path",
            self.settings_grid_layout,
            folder_icon=True,
        )
        (
            self.lineEdit_log_file_name,
            self.label_log_file_name_verified_icon,
            self.btn_log_file_name_verify,
            self.hlayout_log_file_name,
        ) = self.uih.create_input_fields(
            "log_file_name",
            "Log File Name:",
            "Save Log File Name",
            self.settings_grid_layout,
        )
        (
            self.lineEdit_log_backup_count,
            self.label_log_backup_count_verified_icon,
            self.btn_log_backup_count_verify,
            self.hlayout_log_backup_count,
        ) = self.uih.create_input_fields(
            "log_backup_count",
            "Log Backup Count:",
            "Save Log Backup Count",
            self.settings_grid_layout,
            field_type="int",
        )
        (
            self.lineEdit_log_file_max_mbs,
            self.label_log_file_max_mbs_verified_icon,
            self.btn_log_file_max_mbs_verify,
            self.hlayout_log_file_max_mbs,
        ) = self.uih.create_input_fields(
            "log_file_max_mbs",
            "Log File Max Mbs:",
            "Save Log File Max Mbs",
            self.settings_grid_layout,
            field_type="int",
        )
        (
            self.lineEdit_log_keep_files_days,
            self.label_log_keep_files_days_verified_icon,
            self.btn_log_keep_files_days_verify,
            self.hlayout_log_keep_files_days,
        ) = self.uih.create_input_fields(
            "log_keep_files_days",
            "Keep Log File Days:",
            "Save Log File Days",
            self.settings_grid_layout,
            field_type="int",
        )

        (
            self.comboBox_dictionary_source,
            self.label_dictionary_source_verified_icon,
            self.btn_dictionary_source_verify,
            self.hlayout_dictionary_source,
        ) = self.uih.create_input_fields(
            "dictionary_source",
            "Dictionary Source:",
            "Save Dictionary Source",
            self.settings_grid_layout,
            lineEdit=False,
            comboBox=["cpod", "mgdb"],
        )
        (
            self.comboBox_auto_save_on_close,
            self.label_auto_save_on_close_verified_icon,
            self.btn_auto_save_on_close_verify,
            self.hlayout_auto_save_on_close,
        ) = self.uih.create_input_fields(
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

        self.btn_anki_audio_path_verify.clicked.connect(
            lambda: self.open_folder_dialog("anki_audio_path")
        )
        self.btn_log_file_path_verify.clicked.connect(
            lambda: self.open_folder_dialog("log_file_path")
        )

        self.btn_log_file_path_folder.clicked.connect(
            lambda: self.open_folder_dialog("log_file_path")
        )
        self.btn_anki_audio_path_folder.clicked.connect(
            lambda: self.open_folder_dialog("anki_audio_path")
        )

    def get_element(self, el_type, key):
        if el_type == "line_edit":

            line_edit = self.field_registery.get_field(f"lineEdit_{key}")
            if not line_edit:
                raise ValueError(f"No line edit found for key '{key}'")
            return line_edit
        elif el_type == "text_edit":
            text_edit = self.field_registery.get_field(f"textEdit_{key}")
            if not text_edit:
                raise ValueError(f"No line edit found for key '{key}'")
            return text_edit

    def get_line_edit_text(self, key):
        line_edit = self.field_registery.get_field(f"lineEdit_{key}")
        if not line_edit:
            raise ValueError(f"No line edit found for key '{key}'")
        return line_edit.text()

    def get_combo_box_text(self, key):
        combo_box = self.field_registery.get_field(f"comboBox_{key}")
        if not combo_box:
            raise ValueError(f"No line edit found for key '{key}'")
        return combo_box.currentText()

    def get_text_edit_text(self, key):
        textEdit = self.field_registery.get_field(f"textEdit_{key}")
        if not textEdit:
            raise ValueError(f"No line edit found for key '{key}'")
        return textEdit.toPlainText()

    def google_auth_paste_text(self):
        """Handle pasting only."""
        print("here")
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        self.textEdit_google_api_key.setText(text)
        self.secure_setting_change.emit("google_api_key", text)

    def open_folder_dialog(self, key) -> None:
        """
        Opens a dialog for the user to select a folder for storing log files.
        Once a folder is selected, the path is updated in the corresponding input field.

        Returns:
            None: This function does not return a value.
        """
        line_edit = self.field_registery.get_field(f"lineEdit_{key}")
        path = line_edit.text() or "./"

        folder = QFileDialog.getExistingDirectory(self, "Select Folder", dir=path)

        if folder:
            folder = folder if folder[-1] == "/" else folder + "/"
            line_edit.blockSignals(True)
            line_edit.setText(folder)
            line_edit.blockSignals(False)
            self.folder_submit.emit(key, folder)
