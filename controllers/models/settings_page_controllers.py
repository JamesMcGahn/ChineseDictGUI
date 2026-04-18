from dataclasses import dataclass

from ..settings_controller import SettingsController


@dataclass
class SettingsPageControllers:
    settings: SettingsController
