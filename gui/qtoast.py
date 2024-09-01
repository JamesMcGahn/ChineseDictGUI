from pyqttoast import Toast
from PySide6.QtGui import QColor, QFont


class QToast(Toast):
    def __init__(self, parent):
        super().__init__()
        self.setDuration(5000)

        font = QFont([".AppleSystemUIFont"], 12, QFont.Weight.Bold)
        self.setTitleFont(font)
        self.setTextFont(font)
        self.setTextColor(QColor("#ffffff"))
        self.setTitleColor(QColor("#FFFFFF"))
        self.setBackgroundColor(QColor("#000000"))
        self.setDurationBarColor(QColor("#ff0000"))
        self.setIconSeparatorColor(QColor("#000000"))
        self.setMinimumWidth(300)
        self.setMinimumHeight(55)
        self.setBorderRadius(3)
