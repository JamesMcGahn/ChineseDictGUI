from header_navbar import HeaderNavBar
from icon_only_navbar import IconOnlyNavBar
from icon_text_navbar import IconTextNavBar
from main_screen_widget import MainScreenWidget
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QWidget


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("centralwidget")
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        with open("./gui/styles/central_widget.css", "r") as ss:
            self.setStyleSheet(ss.read())
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.icon_only_widget = IconOnlyNavBar()

        self.icon_text_widget = IconTextNavBar()

        self.header_widget = HeaderNavBar()
        self.main_screen_widget = MainScreenWidget()
        self.gridLayout.addWidget(self.main_screen_widget, 2, 3, 1, 1)
        self.gridLayout.addWidget(self.icon_only_widget, 0, 1, 3, 1)
        self.gridLayout.addWidget(self.icon_text_widget, 0, 2, 3, 1)
        self.gridLayout.addWidget(self.header_widget, 0, 3, 1, 1)
        self.setLayout(self.gridLayout)

        self.header_widget.hamburger_signal.connect(self.icon_only_widget.hide_nav)
        self.header_widget.hamburger_signal.connect(self.icon_text_widget.hide_nav)
