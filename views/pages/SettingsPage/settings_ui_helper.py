from PySide6.QtCore import QObject, QSize, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
)

from base import QSingleton
from models.settings import AppSettingsModel
from services.settings import SecureCredentials

from .field_registry import FieldRegistry


class SettingsUIHelper(QObject):
    send_to_verify = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.field_registery = FieldRegistry()
        self.app_settings = AppSettingsModel()

        self.timers = {}

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

    def change_icon_button(self, button, verified=False):
        button.setIcon(self.check_icon if verified else self.x_icon)

    @Slot(str, bool)
    def verify_response_update(self, key, verified):
        print("ssss11111")
        icon_label = self.field_registery.get_field(f"label_{key}_verified_icon")
        verify_btn = self.field_registery.get_field(f"btn_{key}_verify")
        if verified:
            self.change_icon_button(icon_label, True)
            verify_btn.setDisabled(True)
        else:
            self.change_icon_button(icon_label, False)
            verify_btn.setDisabled(False)

    @Slot(str)
    def handle_setting_change_update(self, key):
        icon_label = self.field_registery.get_field(f"label_{key}_verified_icon")
        self.change_icon_button(icon_label, False)

        verify_btn = self.field_registery.get_field(f"btn_{key}_verify")
        verify_btn.setDisabled(False)

    @Slot(str, bool)
    def set_verify_btn_disable(self, key, disable):
        verify_btn = self.field_registery.get_field(f"btn_{key}_verify")
        verify_btn.setDisabled(disable)

    def handle_verify(self, key, value=None):
        print("ee", key, value)
        self.send_to_verify.emit(key, value)

    def create_input_fields(
        self,
        key,
        label_text,
        verify_button_text,
        settings_grid_layout,
        lineEdit=True,
        folder_icon=False,
        comboBox=False,
        field_type="str",
        secure_setting=False,
    ):
        print(key)
        value, verified = self.app_settings.get_setting(key)
        last_row = settings_grid_layout.count() // 4
        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignLeft)

        label = QLabel(label_text)
        label.setMinimumWidth(143)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        label.setStyleSheet("color:white;")

        verify_icon_button = QPushButton()
        self.field_registery.register_field(
            f"label_{key}_verified_icon", verify_icon_button
        )
        verify_icon_button.setMaximumWidth(40)
        verify_icon_button.setStyleSheet("background:transparent;border: none;")
        verify_icon_button.setIcon(self.check_icon if verified else self.x_icon)
        verify_button = QPushButton(verify_button_text)
        self.field_registery.register_field(f"btn_{key}_verify", verify_button)
        verify_button.setCursor(Qt.PointingHandCursor)

        if isinstance(verified, bool):
            verify_button.setDisabled(verified)
        else:
            verify_button.setDisabled(False)

        settings_grid_layout.addWidget(label, last_row, 0, Qt.AlignTop)

        if folder_icon:
            folder_icon_button = QPushButton()
            self.field_registery.register_field(f"btn_{key}_folder", folder_icon_button)
            folder_icon_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            folder_icon_button.setStyleSheet(
                "background:transparent;border: none; margin: 0px; padding: 0px;"
            )

            folder_icon_button.setCursor(Qt.PointingHandCursor)

            folder_icon_button.setIcon(self.folder_icon)
            folder_icon_button.clicked.connect(lambda: self.open_folder_dialog(key))
            verify_button.clicked.connect(lambda: self.open_folder_dialog(key))
        else:
            verify_button.clicked.connect(lambda: self.handle_verify(key))

        if lineEdit:
            line_edit_field = QLineEdit()
            self.field_registery.register_field(f"lineEdit_{key}", line_edit_field)
            print(key, value)
            line_edit_field.setText(str(value))

            h_layout.addWidget(line_edit_field)
            line_edit_field.textChanged.connect(
                lambda word, key=key, field_type=field_type, secure=secure_setting: self.handle_text_change_timer(
                    key, word, field_type, secure
                )
            )
            if folder_icon:
                h_layout.addWidget(folder_icon_button)
            settings_grid_layout.addLayout(h_layout, last_row, 1, Qt.AlignTop)
        elif comboBox and len(comboBox) > 0:
            comboBox_widget = QComboBox()
            self.field_registery.register_field(f"comboBox_{key}", comboBox_widget)
            comboBox_widget.addItems(comboBox)
            comboBox_widget.setCurrentText(str(value))
            h_layout.addWidget(comboBox_widget)
            settings_grid_layout.addLayout(h_layout, last_row, 1, Qt.AlignTop)
            comboBox_widget.currentIndexChanged.connect(
                lambda index, key=key, type="bool": self.onComboBox_changed(
                    index, key, type
                )
            )
        else:
            h_layout = QVBoxLayout()
            text_edit_field = QTextEdit()
            self.field_registery.register_field(f"textEdit_{key}", text_edit_field)
            text_edit_field.setText(value)
            h_layout.addWidget(text_edit_field)
            settings_grid_layout.addLayout(h_layout, last_row, 1, Qt.AlignTop)

        settings_grid_layout.addWidget(verify_icon_button, last_row, 2, Qt.AlignTop)
        settings_grid_layout.addWidget(verify_button, last_row, 3, Qt.AlignTop)

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

    def handle_setting_change(self, key, word, field_type="str"):
        """
        Handles the setting change: saves the new value and updates the icon.

        Args:
            key (str): The field name for the setting.
            word (str): The new value of the setting.
            icon_label (QLabel): The icon label to update.
        """

        self.app_settings.change_setting(key, word, type=field_type)
        self.handle_setting_change_update(key)

    def handle_text_change_timer(self, key, text, field_type, secure=False):
        if key in self.timers:
            self.timers[key].stop()

        self.timers[key] = QTimer(self)
        self.timers[key].setSingleShot(True)
        if secure:
            self.timers[key].timeout.connect(
                lambda: self.handle_secure_user_done_typing(key, text)
            )
        else:
            self.timers[key].timeout.connect(
                lambda: self.handle_setting_change(key, text, field_type)
            )

        self.timers[key].start(500)

    def onComboBox_changed(self, _, key, field_type="str"):
        selected_text = self.field_registery.get_field(f"comboBox_{key}").currentText()
        self.handle_setting_change(key, selected_text, field_type)

    def handle_secure_setting_change(self, field, word):
        self.app_settings.change_secure_setting(field, word)
        self.handle_setting_change_update(field)

    def open_folder_dialog(self, key) -> None:
        """
        Opens a dialog for the user to select a folder for storing log files.
        Once a folder is selected, the path is updated in the corresponding input field.

        Returns:
            None: This function does not return a value.
        """

        line_edit = self.field_registery.get_field(f"lineEdit_{key}")
        path = line_edit.text() or "./"

        folder = QFileDialog.getExistingDirectory(caption="Select Folder", dir=path)

        if folder:
            folder = folder if folder[-1] == "/" else folder + "/"
            line_edit.blockSignals(True)
            line_edit.setText(folder)
            line_edit.blockSignals(False)
            self.handle_verify(key, folder)
