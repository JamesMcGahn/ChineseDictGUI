from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.settings.models import LogSettings

from PySide6.QtCore import Signal, Slot

from base import QWidgetBase
from services.settings.enums import SETTINGSCATEGORIES
from services.settings.models import LogSettings

from .tab_settings_ui import TabLogSettingsUI
from .tab_ui_helper import SettingsUIHelper


class TabSettingsBase(QWidgetBase):
    settings_field_updated = Signal(str, str, object)
    send_to_verify = Signal(str, str, str)
    verify_response_update = Signal(str, str, bool)
    change_verify_btn_disable = Signal(str, str, bool)

    def __init__(
        self,
        tab_id: SETTINGSCATEGORIES,
        settings: LogSettings,
        settings_verify,
        field_registry,
    ):
        super().__init__()
        self.tab_id = tab_id
        self.field_registry = field_registry

        self.sui = SettingsUIHelper(settings_verify, field_registry)
        self.view = TabLogSettingsUI(self.tab_id, settings, self.sui)
        self.layout.addWidget(self.view)

        # SIGNAL CONNECTIONS
        self.sui.send_to_verify.connect(self.send_to_verify)
        self.verify_response_update.connect(self.sui.verify_response_update)
        self.sui.settings_field_updated.connect(self.settings_field_updated)

    def on_verify_response(self, tab, field, is_valid):
        if tab == self.tab_id:
            self.change_verify_btn_disable.emit(tab, field, False)
            self.verify_response_update.emit(tab, field, is_valid)
