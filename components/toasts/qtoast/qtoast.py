from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget
    from .enums import QTOASTSTATUS

from PySide6.QtGui import QColor, QFont

from .pyqttoast import Toast, ToastPosition


class QToast(Toast):

    def __init__(self, parent: QWidget, status: QTOASTSTATUS, title: str, message: str):
        super().__init__(parent=parent)
        self.setDuration(5000)
        self.message = message
        self.title = title
        self.status = status

        font = QFont([".AppleSystemUIFont"], 12, QFont.Weight.Bold)
        self.setTitleFont(font)
        self.setTextFont(font)
        print(self.status)

        self.applyPreset(self.status)
        self.setTextColor(QColor("#ffffff"))
        self.setTitleColor(QColor("#FFFFFF"))
        self.setBackgroundColor(QColor("#000000"))
        self.setDurationBarColor(QColor("#ff0000"))
        self.setIconSeparatorColor(QColor("#000000"))
        self.setIconColor(QColor("#ff0000"))
        self.setCloseButtonIconColor(QColor("#ff0000"))
        self.setMinimumWidth(300)
        self.setMaximumWidth(350)
        self.setMinimumHeight(55)
        self.setBorderRadius(3)
        self.setPosition(ToastPosition.TOP_RIGHT)
        self.setTitle(self.title)
        self.setText(self.message)
