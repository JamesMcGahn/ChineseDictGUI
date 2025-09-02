import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from .central_widget_ui import CentralWidgetView


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = CentralWidgetView()
        wrap = QVBoxLayout(self)
        wrap.setContentsMargins(0, 0, 0, 0)
        wrap.addWidget(self.ui)

        self.setObjectName("centralwidget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "central_widget.css")
        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())

        self.ui.header_widget.hamburger_signal.connect(
            self.ui.icon_only_widget.hide_nav
        )
        self.ui.header_widget.hamburger_signal.connect(
            self.ui.icon_text_widget.hide_nav
        )

        self.ui.icon_only_widget.btn_checked_ico.connect(
            self.ui.icon_text_widget.btns_set_checked
        )
        self.ui.icon_text_widget.btn_checked_ict.connect(
            self.ui.icon_only_widget.btns_set_checked
        )

        self.ui.icon_only_widget.btn_clicked_page.connect(
            self.ui.main_screen_widget.change_page
        )
        self.ui.icon_text_widget.btn_clicked_page.connect(
            self.ui.main_screen_widget.change_page
        )
