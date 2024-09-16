from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QSizePolicy, QWidget


class ColoredSpacer(QWidget):
    def __init__(
        self,
        color,
        width=0,
        height=0,
        hsizePolicy=QSizePolicy.Expanding,
        vsizePolicy=QSizePolicy.Expanding,
    ):
        super().__init__()
        self.color = color
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)
        self.setSizePolicy(hsizePolicy, vsizePolicy)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(self.color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
