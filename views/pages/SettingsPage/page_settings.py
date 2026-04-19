from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.models import SettingsPageControllers

from PySide6.QtCore import Signal

from base import QWidgetBase
from services.settings.enums import SETTINGSCATEGORIES

from ...base import FieldRegistry
from .page_settings_ui import PageSettingsUI
from .tabs import TabSettingsBase


# TODO: Move all Settings logic to a Settings Service
class PageSettings(QWidgetBase):
    verify_response_update = Signal(str, str, bool)
    settings_field_updated = Signal(str, str, object)

    def __init__(self, controllers: SettingsPageControllers):
        super().__init__()
        self.view = PageSettingsUI()
        self.layout.addWidget(self.view)

        self.field_registery = FieldRegistry()
        self.controllers = controllers
        self.settings_controller = self.controllers.settings
        self.app_settings = self.settings_controller.get_settings()
        self.app_verify = self.settings_controller.get_settings_validation()

        self.tabs_loaded = False
        self.set_up_tabs(self.field_registery, self.app_settings, self.app_verify)

    def set_up_tabs(self, field_registry, app_settings, app_verify):
        if self.tabs_loaded:
            return
        for category in app_settings.get_fields_list():
            category_settings = getattr(app_settings, category.name, None)
            if category_settings is None:
                return
            attr_name = f"{category_settings}_tab"
            setattr(
                self,
                attr_name,
                TabSettingsBase(
                    tab_id=SETTINGSCATEGORIES(category_settings.schema_name),
                    settings=category_settings,
                    settings_verify=app_verify[category_settings.schema_name],
                    field_registry=field_registry,
                ),
            )

            self.view.add_page_to_tab(
                getattr(self, attr_name), category_settings.display_name
            )

            getattr(self, attr_name).settings_field_updated.connect(
                self.settings_controller.on_field_change
            )

            getattr(self, attr_name).send_to_verify.connect(
                self.settings_controller.on_field_verify
            )
            self.settings_controller.verify_response_update.connect(
                getattr(self, attr_name).on_verify_response
            )
