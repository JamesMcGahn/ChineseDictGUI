from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from context import AppContext

from .models import SettingsPageControllers


class ControllerFactory:
    def __init__(self, context: AppContext):
        self.ctx = context

    def create_settings_page(self) -> SettingsPageControllers:
        return SettingsPageControllers(settings=self.ctx.settings_controller)
