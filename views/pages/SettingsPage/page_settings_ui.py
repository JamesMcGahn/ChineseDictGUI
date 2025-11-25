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
    QWidget,
)

from components.utils import ColoredSpacer
from models.settings import AppSettingsModel


class PageSettingsUI(QWidget):
    folder_submit = Signal(str, str)
    secure_setting_change = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.settings_page_layout = QHBoxLayout(self)

        self.app_settings = AppSettingsModel()
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

        self.x_icon = QIcon()
        self.x_icon.addFile(
            ":/images/red_check.png",
            QSize(),
            QIcon.Mode.Normal,
        )
        self.check_icon = QIcon()
        self.check_icon.addFile(
            ":/images/green_check.png",
            QSize(),
            QIcon.Mode.Normal,
        )
        self.folder_icon = QIcon()
        self.folder_icon.addFile(
            ":/images/open_folder_on.png",
            QSize(),
            QIcon.Mode.Normal,
        )

        self.settings_page_layout.addItem(self.hspacer1)
        (
            self.lineEdit_apple_note_name,
            self.label_apple_note_name_verified_icon,
            self.btn_apple_note_name_verify,
            self.hlayout_apple_note_name,
        ) = self.create_input_fields(
            "apple_note_name", "Apple Note Name:", "Verify Apple Note"
        )
        (
            self.lineEdit_anki_words_deck_name,
            self.label_anki_words_deck_name_verified_icon,
            self.btn_anki_words_deck_name_verify,
            self.hlayout_anki_words_deck_name,
        ) = self.create_input_fields(
            "anki_words_deck_name", "Word's Deck Name:", "Verify Deck"
        )
        (
            self.lineEdit_anki_sents_deck_name,
            self.label_anki_sents_deck_name_verified_icon,
            self.btn_anki_sents_deck_name_verify,
            self.hlayout_sents_anki_deck_name,
        ) = self.create_input_fields(
            "anki_sents_deck_name", "Sents's Deck Name:", "Verify Deck"
        )

        (
            self.lineEdit_anki_words_model_name,
            self.label_anki_words_model_name_verified_icon,
            self.btn_anki_words_model_name_verify,
            self.hlayout_anki_words_model_name,
        ) = self.create_input_fields(
            "anki_words_model_name", "Word's Model Name:", "Verify Model"
        )
        (
            self.lineEdit_anki_sents_model_name,
            self.label_anki_sents_model_name_verified_icon,
            self.btn_anki_sents_model_name_verify,
            self.hlayout_anki_sents_model_name,
        ) = self.create_input_fields(
            "anki_sents_model_name", "Sent's Model Name:", "Verify Model"
        )

        (
            self.lineEdit_anki_user,
            self.label_anki_user_verified_icon,
            self.btn_anki_user_verify,
            self.hlayout_anki_user,
        ) = self.create_input_fields("anki_user", "Anki User Name:", "Verify User")
        (
            self.lineEdit_anki_audio_path,
            self.label_anki_audio_path_verified_icon,
            self.btn_anki_audio_path_verify,
            self.hlayout_anki_audio_path,
            self.btn_anki_audio_path_folder,
        ) = self.create_input_fields(
            "anki_audio_path", "Anki Audio path:", "Verify Audio Path", folder_icon=True
        )
        (
            self.lineEdit_log_file_path,
            self.label_log_file_path_verified_icon,
            self.btn_log_file_path_verify,
            self.hlayout_log_file_path,
            self.btn_log_file_path_folder,
        ) = self.create_input_fields(
            "log_file_path", "Log File path:", "Verify Log Path", folder_icon=True
        )
        (
            self.lineEdit_log_file_name,
            self.label_log_file_name_verified_icon,
            self.btn_log_file_name_verify,
            self.hlayout_log_file_name,
        ) = self.create_input_fields(
            "log_file_name", "Log File Name:", "Save Log File Name"
        )
        (
            self.lineEdit_log_backup_count,
            self.label_log_backup_count_verified_icon,
            self.btn_log_backup_count_verify,
            self.hlayout_log_backup_count,
        ) = self.create_input_fields(
            "log_backup_count", "Log Backup Count:", "Save Log Backup Count"
        )
        (
            self.lineEdit_log_file_max_mbs,
            self.label_log_file_max_mbs_verified_icon,
            self.btn_log_file_max_mbs_verify,
            self.hlayout_log_file_max_mbs,
        ) = self.create_input_fields(
            "log_file_max_mbs", "Log File Max Mbs:", "Save Log File Max Mbs"
        )
        (
            self.lineEdit_log_keep_files_days,
            self.label_log_keep_files_days_verified_icon,
            self.btn_log_keep_files_days_verify,
            self.hlayout_log_keep_files_days,
        ) = self.create_input_fields(
            "log_keep_files_days", "Keep Log File Days:", "Save Log File Days"
        )

        (
            self.comboBox_dictionary_source,
            self.label_dictionary_source_verified_icon,
            self.btn_dictionary_source_verify,
            self.hlayout_dictionary_source,
        ) = self.create_input_fields(
            "dictionary_source",
            "Dictionary Source:",
            "Save Dictionary Source",
            lineEdit=False,
            comboBox=["cpod", "mgdb"],
        )
        (
            self.comboBox_auto_save_on_close,
            self.label_auto_save_on_close_verified_icon,
            self.btn_auto_save_on_close_verify,
            self.hlayout_auto_save_on_close,
        ) = self.create_input_fields(
            "auto_save_on_close",
            "Auto Save on Close:",
            "Save Auto Close",
            lineEdit=False,
            comboBox=["True", "False"],
        )

        (
            self.textEdit_google_api_key,
            self.label_google_api_key_verified_icon,
            self.btn_google_api_key_verify,
            self.vlayout_google_api_key,
        ) = self.create_input_fields(
            "google_api_key", "Google Service:", "Verify Google Service", False
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

    def get_line_edit_text(self, key):
        line_edit = getattr(self, f"lineEdit_{key}")
        if not line_edit:
            raise ValueError(f"No line edit found for key '{key}'")
        return line_edit.text()

    def get_combo_box_text(self, key):
        combo_box = getattr(self, f"comboBox_{key}")
        if not combo_box:
            raise ValueError(f"No line edit found for key '{key}'")
        return combo_box.currentText()

    def get_text_edit_text(self, key):
        textEdit = getattr(self, f"textEdit_{key}")
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

    def create_input_fields(
        self,
        key,
        label_text,
        verify_button_text,
        lineEdit=True,
        folder_icon=False,
        comboBox=False,
    ):

        value, verified = self.app_settings.get_setting(key)
        last_row = self.settings_grid_layout.count() // self.columns
        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignLeft)

        label = QLabel(label_text)
        label.setMinimumWidth(143)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        label.setStyleSheet("color:white;")

        verify_icon_button = QPushButton()
        verify_icon_button.setMaximumWidth(40)
        verify_icon_button.setStyleSheet("background:transparent;border: none;")
        verify_icon_button.setIcon(self.check_icon if verified else self.x_icon)
        verify_button = QPushButton(verify_button_text)
        verify_button.setCursor(Qt.PointingHandCursor)
        if isinstance(verified, bool):
            verify_button.setDisabled(verified)
        else:
            verify_button.setDisabled(False)

        self.settings_grid_layout.addWidget(label, last_row, 0, Qt.AlignTop)

        if folder_icon:
            folder_icon_button = QPushButton()
            folder_icon_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            folder_icon_button.setStyleSheet(
                "background:transparent;border: none; margin: 0px; padding: 0px;"
            )

            folder_icon_button.setCursor(Qt.PointingHandCursor)

            folder_icon_button.setIcon(self.folder_icon)

        if lineEdit:
            line_edit_field = QLineEdit()
            line_edit_field.setText(str(value))
            h_layout.addWidget(line_edit_field)
            if folder_icon:
                h_layout.addWidget(folder_icon_button)
            self.settings_grid_layout.addLayout(h_layout, last_row, 1, Qt.AlignTop)
        elif comboBox and len(comboBox) > 0:
            comboBox_widget = QComboBox()
            comboBox_widget.addItems(comboBox)
            comboBox_widget.setCurrentText(str(value))
            h_layout.addWidget(comboBox_widget)
            self.settings_grid_layout.addLayout(h_layout, last_row, 1, Qt.AlignTop)
        else:
            h_layout = QVBoxLayout()
            text_edit_field = QTextEdit()
            text_edit_field.setText(value)
            h_layout.addWidget(text_edit_field)
            self.settings_grid_layout.addLayout(h_layout, last_row, 1, Qt.AlignTop)

        self.settings_grid_layout.addWidget(
            verify_icon_button, last_row, 2, Qt.AlignTop
        )
        self.settings_grid_layout.addWidget(verify_button, last_row, 3, Qt.AlignTop)

        if folder_icon:
            return (
                line_edit_field if lineEdit else text_edit_field,
                verify_icon_button,
                verify_button,
                h_layout,
                folder_icon_button,
            )
        return (
            (
                line_edit_field
                if lineEdit
                else comboBox_widget if comboBox else text_edit_field
            ),
            verify_icon_button,
            verify_button,
            h_layout,
        )

    def change_icon_button(self, button, verified=False):
        button.setIcon(self.check_icon if verified else self.x_icon)

    @Slot(str, bool)
    def verify_response_update(self, key, verified):
        icon_label = getattr(self, f"label_{key}_verified_icon")
        verify_btn = getattr(self, f"btn_{key}_verify")
        if verified:
            self.change_icon_button(icon_label, True)
            verify_btn.setDisabled(True)
        else:
            self.change_icon_button(icon_label, False)
            verify_btn.setDisabled(False)

    @Slot(str)
    def handle_setting_change_update(self, key):
        icon_label = getattr(self, f"label_{key}_verified_icon")
        self.change_icon_button(icon_label, False)

        verify_btn = getattr(self, f"btn_{key}_verify")
        verify_btn.setDisabled(False)

    @Slot(str, bool)
    def set_verify_btn_disable(self, key, disable):
        verify_btn = getattr(self, f"btn_{key}_verify")
        verify_btn.setDisabled(disable)

    def open_folder_dialog(self, key) -> None:
        """
        Opens a dialog for the user to select a folder for storing log files.
        Once a folder is selected, the path is updated in the corresponding input field.

        Returns:
            None: This function does not return a value.
        """
        line_edit = getattr(self, f"lineEdit_{key}")
        path = line_edit.text() or "./"

        folder = QFileDialog.getExistingDirectory(self, "Select Folder", dir=path)

        if folder:
            folder = folder if folder[-1] == "/" else folder + "/"
            line_edit.blockSignals(True)
            line_edit.setText(folder)
            line_edit.blockSignals(False)
            self.folder_submit.emit(key, folder)


# class PageSettingsUI(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.init_ui()

#     def init_ui(self):
#         self.setObjectName("settings_page_ui")
#         self.label_6 = QLabel()
#         self.label_6.setObjectName("label_6")
#         self.label_6.setGeometry(QRect(280, 330, 221, 81))
#         self.label_6.setText("Settings page")
#         font1 = QFont()

#         font1.setPointSize(25)
#         self.label_6.setFont(font1)

#         hspacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
#         hspacer1 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
#         vspacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
#         vspacer1 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

#         # colored_spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)

#         self.anki_deck_widget = QWidget()
#         self.anki_deck_widget.setObjectName("anki_deck_widget")
#         # self.anki_deck_widget.setMaximumSize(QSize(700, 200))
#         self.anki_deck_widget.setMinimumSize(QSize(500, 200))
#         # Anki Deck Layout
#         self.anki_deck_vlayout = QVBoxLayout()
#         self.anki_deck_vlayout.setSpacing(5)

#         # Words Deck Labels
#         self.label_anki_words_deck = QLabel("Word's Deck Name:")
#         self.label_anki_words_deck.setMinimumWidth(143)
#         self.lineEdit_anki_words_deck = QLineEdit()
#         self.lineEdit_anki_words_deck.setMaximumWidth(230)
#         self.label_anki_words_deck_verfied = QPushButton()
#         self.label_anki_words_deck_verfied.setMinimumWidth(20)
#         self.label_anki_words_deck_verfied.setObjectName("anki_verify_icon_w")
#         self.x_icon = QIcon()
#         self.x_icon.addFile(
#             ":/ /images/red_check.png",
#             QSize(),
#             QIcon.Mode.Normal,
#         )
#         self.check_icon = QIcon()
#         self.check_icon.addFile(
#             ":/ /images/green_check.png",
#             QSize(),
#             QIcon.Mode.Normal,
#         )
#         self.folder_icon = QIcon()
#         self.folder_icon.addFile(
#             ":/images/open_folder_on.png",
#             QSize(),
#             QIcon.Mode.Normal,
#         )

#         self.label_anki_words_verify_btn = QPushButton("Verify Deck")

#         self.anki_words_deck_hlayout = QHBoxLayout()
#         self.anki_words_deck_hlayout.setSpacing(10)
#         # self.anki_words_deck_hlayout.addItem(hspacer)
#         self.anki_words_deck_hlayout.addWidget(self.label_anki_words_deck)
#         self.anki_words_deck_hlayout.addWidget(self.lineEdit_anki_words_deck)
#         self.anki_words_deck_hlayout.addWidget(self.label_anki_words_deck_verfied)
#         self.anki_words_deck_hlayout.addWidget(self.label_anki_words_verify_btn)
#         # self.anki_words_deck_hlayout.addItem(hspacer)

#         # Sents Deck Labels
#         self.label_anki_sents_deck = QLabel("Sentence's Deck Name:")
#         self.label_anki_sents_deck.setMinimumWidth(143)
#         self.lineEdit_anki_sents_deck = QLineEdit()
#         self.lineEdit_anki_sents_deck.setMaximumWidth(230)
#         self.label_anki_sents_deck_verfied = QPushButton()
#         self.label_anki_sents_deck_verfied.setMinimumWidth(20)
#         self.label_anki_sents_deck_verfied.setObjectName("anki_verify_icon_s")
#         self.label_anki_sents_verify_btn = QPushButton("Verify Deck")

#         self.anki_sents_deck_hlayout = QHBoxLayout()
#         self.anki_sents_deck_hlayout.setSpacing(10)
#         # self.anki_sents_deck_hlayout.addItem(hspacer)
#         self.anki_sents_deck_hlayout.addWidget(self.label_anki_sents_deck)
#         self.anki_sents_deck_hlayout.addWidget(self.lineEdit_anki_sents_deck)
#         self.anki_sents_deck_hlayout.addWidget(self.label_anki_sents_deck_verfied)
#         self.anki_sents_deck_hlayout.addWidget(self.label_anki_sents_verify_btn)
#         # self.anki_sents_deck_hlayout.addItem(hspacer)

#         # self.anki_deck_vlayout.addItem(vspacer)
#         spacer1 = ColoredSpacer(
#             "red", 400, 1, QSizePolicy.Expanding, QSizePolicy.Minimum
#         )
#         self.anki_deck_vlayout.addWidget(spacer1)
#         self.anki_deck_vlayout.addLayout(self.anki_words_deck_hlayout)
#         self.anki_deck_vlayout.addLayout(self.anki_sents_deck_hlayout)
#         self.anki_deck_vlayout.addItem(vspacer)

#         self.anki_deck_widget.setLayout(self.anki_deck_vlayout)

#         self.settings_page_vlayout = QVBoxLayout(self)
#         self.settings_page_vlayout.setSpacing(2)
#         self.settings_page_vlayout.addWidget(self.label_6)
#         anki_widget_hlayout = QHBoxLayout()
#         anki_widget_hlayout.addItem(hspacer)
#         anki_widget_hlayout.addWidget(self.anki_deck_widget)
#         anki_widget_hlayout.addItem(hspacer1)
#         self.settings_page_vlayout.addLayout(anki_widget_hlayout)

#         self.import_deck_btn = QPushButton("Import Deck From Anki")

#         self.settings_page_vlayout.addWidget(self.import_deck_btn)

#         self.sync_import_btn = QPushButton("Test Import Sync")

#         self.settings_page_vlayout.addWidget(self.sync_import_btn)

#         self.sync_export_btn = QPushButton("Test Export Sync")

#         self.settings_page_vlayout.addWidget(self.sync_export_btn)
#         self.settings_page_vlayout.addItem(vspacer1)
