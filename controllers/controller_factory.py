from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from context import AppContext

from .models import ImportPageControllers, SettingsPageControllers


class ControllerFactory:
    def __init__(self, context: AppContext):
        self.ctx = context

    def create_settings_page(self) -> SettingsPageControllers:
        return SettingsPageControllers(settings=self.ctx.settings_controller)

    def create_import_page(self) -> ImportPageControllers:
        return ImportPageControllers(lessons=self.ctx.lessons_controller)
