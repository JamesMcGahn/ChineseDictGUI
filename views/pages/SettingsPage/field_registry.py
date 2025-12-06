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

    def get_line_edit_text(self, key, tab=None):
        if tab:
            line_edit = self.get_text_value(f"{tab}/line_edit_{key}")
        else:
            line_edit = self.get_text_value(f"line_edit_{key}")
        return line_edit

    def get_combo_box_text(self, key, tab=None):
        if tab:
            combo_box = self.get_text_value(f"{tab}/combo_box_{key}")
        else:
            combo_box = self.get_text_value(f"combo_box_{key}")
        return combo_box

    def get_text_edit_text(self, key, tab=None):
        if tab:
            textEdit = self.get_text_value(f"{tab}/text_edit_{key}")
        else:
            textEdit = self.get_text_value(f"text_edit_{key}")
        return textEdit
