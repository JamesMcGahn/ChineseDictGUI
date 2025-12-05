from PySide6.QtCore import QObject
from PySide6.QtWidgets import QComboBox, QLineEdit, QTextEdit

from base import QSingleton


class FieldRegistry(QObject, metaclass=QSingleton):

    def __init__(self):
        super().__init__()
        self.fields = {}

    def register_field(self, key, value):
        self.fields[key] = value

    def get_field(self, key):
        if key not in self.fields:
            raise ValueError("No such key in registry.")
        else:
            return self.fields[key]

    def get_text_value(self, key):
        if key not in self.fields:
            raise ValueError("No such key in registry.")

        widget = self.get_field(key)

        if isinstance(widget, QLineEdit):
            return widget.text()

        if isinstance(widget, QTextEdit):
            return widget.toPlainText()

        if isinstance(widget, QComboBox):
            return widget.currentText()

        raise TypeError(
            f"Widget type {type(widget)} is not supported by get_text_value()"
        )
