from PySide6.QtCore import QObject, QSize, Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
)

from models.settings import AppSettingsModel

from .field_registry import FieldRegistry


class SettingsUIHelper(QObject):

    def __init__(self):
        self.field_registery = FieldRegistry()
        self.app_settings = AppSettingsModel()
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

    def create_input_fields(
        self,
        key,
        label_text,
        verify_button_text,
        settings_grid_layout,
        lineEdit=True,
        folder_icon=False,
        comboBox=False,
    ):

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

        if lineEdit:
            line_edit_field = QLineEdit()
            self.field_registery.register_field(f"lineEdit_{key}", line_edit_field)
            line_edit_field.setText(str(value))
            h_layout.addWidget(line_edit_field)
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
