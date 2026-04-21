from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers import ControllerFactory

from PySide6.QtCore import QRect, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

from base import QWidgetBase

from ..pages import PageDictionary, PageLessons, PageLogs, PageSettings, PageWords
from .main_screen_ui import MainScreenView


class MainScreen(QWidgetBase):

    def __init__(self, controller_factory: ControllerFactory):
        super().__init__()
        self.ui = MainScreenView()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.ui)

        self.setObjectName("main_screen")

        self.controller_factory = controller_factory

        self.settings_page_controllers = self.controller_factory.create_settings_page()
        self.import_page_controllers = self.controller_factory.create_import_page()
        self.audio_page = QWidget()

        self.audio_page.setObjectName("audio_page")
        self.label_2 = QLabel(self.audio_page)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(350, 410, 221, 81))
        font1 = QFont()
        self.label_2.setFont(font1)
        self.label_2.setText("audio page")

        self.words_page = PageWords()
        self.sentences_page = PageLessons(controllers=self.import_page_controllers)
        self.dictionary_page = PageDictionary()
        self.settings_page = PageSettings(controllers=self.settings_page_controllers)
        self.logs_page = PageLogs()

        self.ui.add_page_to_stacked_widget(self.words_page)
        self.ui.add_page_to_stacked_widget(self.sentences_page)
        self.ui.add_page_to_stacked_widget(self.audio_page)
        self.ui.add_page_to_stacked_widget(self.dictionary_page)
        self.ui.add_page_to_stacked_widget(self.settings_page)
        self.ui.add_page_to_stacked_widget(self.logs_page)

        # TODO REMOVE after going to controller - pages shouldnt have services
        self.appshutdown.connect(self.words_page.notified_app_shutting)
        self.appshutdown.connect(self.sentences_page.notified_app_shutting)
        self.appshutdown.connect(self.dictionary_page.notified_app_shutting)
        self.appshutdown.connect(self.settings_page.notified_app_shutting)
        self.appshutdown.connect(self.logs_page.notified_app_shutting)

    @Slot(QPushButton)
    def change_page(self, btn):
        btn_name = btn.objectName()

        if btn_name.startswith("words_btn_"):
            self.ui.stackedWidget.setCurrentIndex(0)
        elif btn_name.startswith("sents_btn_"):
            self.ui.stackedWidget.setCurrentIndex(1)
        elif btn_name.startswith("audio_btn_"):
            self.ui.stackedWidget.setCurrentIndex(2)
        elif btn_name.startswith("dictionary_btn_"):
            self.ui.stackedWidget.setCurrentIndex(3)
        elif btn_name.startswith("settings_btn_"):
            self.ui.stackedWidget.setCurrentIndex(4)
        elif btn_name.startswith("logs_btn_"):
            self.ui.stackedWidget.setCurrentIndex(5)
