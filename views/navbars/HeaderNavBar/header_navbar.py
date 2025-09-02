import os

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from .header_navbar_ui import HeaderNavBarView


class HeaderNavBar(QWidget):
    hamburger_signal = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setObjectName("header_widget")
        self.setMaximumSize(QSize(16777215, 175))
        self.setAttribute(Qt.WA_StyledBackground, True)
        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "header_navbar.css")

        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())

        self.ui = HeaderNavBarView()
        wrap = QVBoxLayout(self)
        wrap.setContentsMargins(0, 0, 0, 0)
        wrap.addWidget(self.ui)

        self.ui.hamburger_icon_btn.toggled.connect(self.hamburger_icon_btn_toggled)

    def hamburger_icon_btn_toggled(self):
        self.hamburger_signal.emit(self.ui.hamburger_icon_btn.isChecked())
