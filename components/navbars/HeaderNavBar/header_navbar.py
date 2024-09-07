from PySide6.QtCore import QObject, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from .header_navbar_ui import HeaderNavBarView


class HeaderNavBar(QWidget):
    hamburger_signal = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setObjectName("header_widget")

        self.ui = HeaderNavBarView()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.ui)
        self.setLayout(self.layout)

        self.ui.hamburger_icon_btn.toggled.connect(self.hamburger_icon_btn_toggled)

    def hamburger_icon_btn_toggled(self):
        self.hamburger_signal.emit(self.ui.hamburger_icon_btn.isChecked())
