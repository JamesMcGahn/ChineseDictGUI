from PySide6.QtCore import QSettings

from utils import Singleton


class AppSettings(Singleton):
    def __init__(self):
        super().__init__()
        self._settings = QSettings("ChineseDict", "ChineseDictApp")

    def set_value(self, key, value):
        self._settings.setValue(key, value)

    def get_value(self, key, default=None):
        return self._settings.value(key, default)

    def begin_group(self, group):
        self._settings.beginGroup(group)

    def end_group(self):
        self._settings.endGroup()

    def remove(self, key):
        self._settings.remove(key)
