from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.settings.models import LogSettings

from dataclasses import asdict, fields

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from models.settings import settings_mapping

from ...field_registry import FieldRegistry


class TabLogSettingsUI(QWidget):
    folder_submit = Signal(str, str)
    secure_setting_change = Signal(str, str)

    def __init__(self, tab_id, settings: LogSettings, ui_helper):
        super().__init__()
        self.tab_id = tab_id
        self.settings_page_layout = QHBoxLayout(self)
        self.field_registery = FieldRegistry()
        self.settings = settings
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

        # self.fields_to_map = settings_mapping[self.tab_id]

        for field in fields(self.settings):
            key = field.name
            value = getattr(self.settings, key)
            print(key, value, type(value))
            meta = self.settings.get_field_meta(key)
            self.uih.create_input_fields(
                self.tab_id, key, value, meta, self.settings_grid_layout
            )

        self.vspacer2 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vspacer3 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.settings_grid_layout.addItem(
            self.vspacer2, self.settings_grid_layout.count() // self.columns, 2
        )

        self.settings_page_layout.addItem(self.vspacer3)
