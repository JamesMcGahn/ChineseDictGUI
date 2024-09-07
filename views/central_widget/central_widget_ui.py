from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QWidget

from views import MainScreen
from views.navbars import HeaderNavBar, IconOnlyNavBar, IconTextNavBar


class CentralWidgetView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.icon_only_widget = IconOnlyNavBar()

        self.icon_text_widget = IconTextNavBar()

        self.header_widget = HeaderNavBar()
        self.main_screen_widget = MainScreen()
        self.gridLayout.addWidget(self.main_screen_widget, 2, 3, 1, 1)
        self.gridLayout.addWidget(self.icon_only_widget, 0, 1, 3, 1)
        self.gridLayout.addWidget(self.icon_text_widget, 0, 2, 3, 1)
        self.gridLayout.addWidget(self.header_widget, 0, 3, 1, 1)
        self.setLayout(self.gridLayout)
