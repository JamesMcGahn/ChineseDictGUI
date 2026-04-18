from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers import ControllerFactory

import os

from PySide6.QtCore import Qt

from base import QWidgetBase

from ..mainscreen import MainScreen
from .central_widget_ui import CentralWidgetView


class CentralWidget(QWidgetBase):

    def __init__(self, controller_factory: ControllerFactory):
        super().__init__()
        self.ui = CentralWidgetView()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.ui)
        self.main_screen_widget = MainScreen(controller_factory=controller_factory)
        self.ui.add_widget_to_grid(self.main_screen_widget, 2, 3, 1, 1)

        self.setObjectName("centralwidget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "central_widget.css")
        self.appshutdown.connect(self.main_screen_widget.notified_app_shutting)

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
            self.main_screen_widget.change_page
        )
        self.ui.icon_text_widget.btn_clicked_page.connect(
            self.main_screen_widget.change_page
        )
