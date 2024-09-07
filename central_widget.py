from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QWidget

from components.navbars import HeaderNavBar, IconOnlyNavBar, IconTextNavBar
from main_screen_widget import MainScreenWidget


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("centralwidget")
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        with open("./styles/central_widget.css", "r") as ss:
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

        self.icon_only_widget.btn_checked_ico.connect(
            self.icon_text_widget.btns_set_checked
        )
        self.icon_text_widget.btn_checked_ict.connect(
            self.icon_only_widget.btns_set_checked
        )

        self.icon_only_widget.btn_clicked_page.connect(
            self.main_screen_widget.change_page
        )
        self.icon_text_widget.btn_clicked_page.connect(
            self.main_screen_widget.change_page
        )
