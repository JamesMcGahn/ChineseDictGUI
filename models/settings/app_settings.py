import os

from PySide6.QtCore import QObject

from base import QSingleton
from services.settings import AppSettings, SecureCredentials


class AppSettingsModel(QObject, metaclass=QSingleton):

    def __init__(self):
        self.settings = AppSettings()
        self.secure_creds = SecureCredentials()

        # ANKI
        self.anki_user = ""
        self.anki_user_verified = False
        self.anki_audio_path = ""
        self.anki_audio_path_verified = False

        self.anki_words_deck_name = ""
        self.anki_sents_deck_name = ""
        self.anki_words_deck_name_verified = False
        self.anki_sents_deck_name_verified = False

        self.anki_words_model_name = ""
        self.anki_sents_model_name = ""
        self.anki_words_model_name_verified = False
        self.anki_sents_model_name_verified = False

        self.apple_note_name = ""
        self.apple_note_name_verified = False

        self.google_api_key = ""
        self.google_api_key_verified = False

        self.dictionary_source = ""
        self.dictionary_source_verified = False

        self.log_file_path_verified = False
        self.log_file_name_verified = False
        self.log_file_max_mbs_verified = False
        self.log_backup_count_verified = False
        self.log_keep_files_days_verified = False

        self.log_file_path = ""
        self.log_file_name = ""
        self.log_file_max_mbs = 5
        self.log_backup_count = 5
        self.log_keep_files_days = 5

        self.home_directory = os.path.expanduser("~")

        self.settings_keys = [
            "anki_words_deck_name",
            "anki_sents_deck_name",
            "anki_words_model_name",
            "anki_sents_model_name",
            "anki_user",
            "anki_audio_path",
            "apple_note_name",
            "google_api_key",
            "log_file_name",
            "log_file_max_mbs",
            "log_file_path",
            "log_keep_files_days",
            "log_backup_count",
            "dictionary_source",
        ]

        self.settings_mapping = {
            "apple_note_name": {
                "default": "",
                "type": "str",
            },
            "anki_words_deck_name": {
                "default": "",
                "type": "str",
            },
            "anki_sents_deck_name": {
                "default": "",
                "type": "str",
            },
            "anki_words_model_name": {
                "default": "",
                "type": "str",
            },
            "anki_sents_model_name": {
                "default": "",
                "type": "str",
            },
            "anki_user": {
                "default": "User 1",
                "type": "str",
            },
            "anki_audio_path": {
                "default": f"{self.home_directory}/Library/Application Support/Anki2/{self.anki_user}/collection.media",
                "type": "str",
            },
            "google_api_key": {
                "default": "{}",
                "type": "secure",
            },
            "log_file_path": {
                "default": "./logs/",
                "type": "str",
            },
            "log_file_name": {
                "default": "file.log",
                "type": "str",
            },
            "log_file_max_mbs": {
                "default": 5,
                "type": "int",
            },
            "log_keep_files_days": {
                "default": 5,
                "type": "int",
            },
            "log_backup_count": {
                "default": 5,
                "type": "int",
            },
            "dictionary_source": {
                "default": "cpod",
                "type": "str",
            },
            "auto_save_on_close": {"default": True, "type": "bool"},
        }

    def get_settings(self):
        """
        Retrieve and update settings values.

        Args:
            setting (str): The specific setting key or "ALL" for all settings.
            set_text (bool): Whether to update the widgets with the retrieved values.
        """
        self.settings.begin_group("settings")
        for key, config in self.settings_mapping.items():

            if config["type"] == "secure":
                value = self.secure_creds.get_creds("chinese-dict-secure-settings", key)
                verified = self.settings.get_value(f"{key}-verified", False)
            else:
                value = self.settings.get_value(key, config["default"])
                verified = self.settings.get_value(f"{key}-verified", False)
            setattr(self, key, value)
            setattr(self, f"{key}_verified", verified)
        self.settings.end_group()

    def get_setting(self, key):
        try:
            value = getattr(self, key)
            verified = getattr(self, f"{key}_verified", False)
            return value, verified
        except AttributeError as e:
            print(f"Error: Attribute '{key}' or '{key}_verified' does not exist. {e}")

    def change_setting(self, key, value, verified=False, type="str"):
        self.settings.begin_group("settings")
        try:
            if type == "int":
                value = int(value if value else 0)
                self.settings.set_value(key, value)
            elif type == "bool":
                value = bool(value.lower() == "true")
                self.settings.set_value(key, value)
            else:
                self.settings.set_value(key, str(value))
            self.settings.set_value(f"{key}-verified", verified)
            setattr(self, key, value)
            setattr(self, f"{key}_verified", verified)
            print("ss", key, value)

        except AttributeError as e:
            print(f"Error: Attribute '{key}' or '{key}_verified' does not exist. {e}")
        self.settings.end_group()

    def change_secure_setting(self, key, value, verified=False):
        print(key, value)
        setattr(self, key, value)
        setattr(self, f"{key}_verified", verified)
        self.secure_creds.save_creds("chinese-dict-secure-settings", key, value)
        self.settings.begin_group("settings")
        self.settings.set_value(f"{key}-verified", verified)
        self.settings.end_group()
