from pyqttoast import Toast, ToastPosition, ToastPreset
from PySide6.QtGui import QColor, QFont


class QToast(Toast):
    def __init__(self, parent, status, title, message):
        super().__init__()
        self.setDuration(5000)
        self.message = message
        self.title = title
        self.status = status

        font = QFont([".AppleSystemUIFont"], 12, QFont.Weight.Bold)
        self.setTitleFont(font)
        self.setTextFont(font)

        match (self.status):
            case "success":
                self.applyPreset(ToastPreset.SUCCESS)
            case "error":
                self.applyPreset(ToastPreset.ERROR)
            case "warning":
                self.applyPreset(ToastPreset.WARNING)
            case "info":
                self.applyPreset(ToastPreset.INFORMATION)
            case "close":
                self.applyPreset(ToastPreset.CLOSE)

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
