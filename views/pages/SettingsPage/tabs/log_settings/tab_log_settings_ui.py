from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from ...field_registry import FieldRegistry


class TabLogSettingsUI(QWidget):
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

        self.vspacer2 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vspacer3 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.settings_grid_layout.addItem(
            self.vspacer2, self.settings_grid_layout.count() // self.columns, 2
        )
