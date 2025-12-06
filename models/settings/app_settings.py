import os

from PySide6.QtCore import QObject

from base import QSingleton
from services.settings import AppSettings, SecureCredentials

from .settings_mapping import settings_mapping


class AppSettingsModel(QObject, metaclass=QSingleton):

    def __init__(self):
        self.settings = AppSettings()
        self.secure_creds = SecureCredentials()

        self.home_directory = os.path.expanduser("~")
        self.settings_mapping = settings_mapping

    def get_settings(self):
        """
        Retrieve and update settings values.

        Args:
            setting (str): The specific setting key or "ALL" for all settings.
            set_text (bool): Whether to update the widgets with the retrieved values.
        """
        self.settings.begin_group("settings")
        for tab_key, tab_configs in self.settings_mapping.items():
            for key, config in tab_configs.items():

                if config["type"] == "secure":
                    value = self.secure_creds.get_creds(
                        "chinese-dict-secure-settings", f"{tab_key}/{key}"
                    )
                    verified = self.settings.get_value(
                        f"{tab_key}/{key}-verified", False
                    )
                else:
                    value = self.settings.get_value(
                        f"{tab_key}/{key}", config["default"]
                    )
                    verified = self.settings.get_value(
                        f"{tab_key}/{key}-verified", False
                    )
                setattr(self, f"{tab_key}/{key}", value)
                setattr(self, f"{tab_key}/{key}_verified", verified)
                print(tab_key, key, value, verified)
        self.settings.end_group()

    def get_setting(self, tab_key, key):
        try:
            value = getattr(self, f"{tab_key}/{key}")
            verified = getattr(self, f"{tab_key}/{key}_verified", False)
            return value, verified
        except AttributeError as e:
            print(
                f"Error: Attribute '{tab_key}/{key}' or '{tab_key}/{key}_verified' does not exist. {e}"
            )

    def change_setting(self, tab_key, key, value, verified=False, type="str"):
        self.settings.begin_group("settings")
        try:
            if type == "int":
                value = int(value if value else 0)
                self.settings.set_value(f"{tab_key}/{key}", value)
            elif type == "bool":
                value = bool(value.lower() == "true")
                self.settings.set_value(f"{tab_key}/{key}", value)
            else:
                self.settings.set_value(f"{tab_key}/{key}", str(value))
            self.settings.set_value(f"{tab_key}/{key}-verified", verified)
            setattr(self, f"{tab_key}/{key}", value)
            setattr(self, f"{tab_key}/{key}_verified", verified)
            print("change_setting", tab_key, key, value)

        except AttributeError as e:
            print(f"Error: Attribute '{key}' or '{key}_verified' does not exist. {e}")
        self.settings.end_group()

    def change_secure_setting(self, tab_key, key, value, verified=False):
        print("change_secure_setting", tab_key, key, value)
        setattr(self, f"{tab_key}/{key}", value)
        setattr(self, f"{key}_verified", verified)
        self.secure_creds.save_creds(
            "chinese-dict-secure-settings", f"{tab_key}/{key}", value
        )
        self.settings.begin_group("settings")
        self.settings.set_value(f"{tab_key}/{key}-verified", verified)
        self.settings.end_group()
