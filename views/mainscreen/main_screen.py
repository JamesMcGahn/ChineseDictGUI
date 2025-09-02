from PySide6.QtCore import Slot
from PySide6.QtWidgets import QPushButton, QVBoxLayout

from base import QWidgetBase

from .main_screen_ui import MainScreenView


class MainScreen(QWidgetBase):
    def __init__(self):
        super().__init__()
        self.ui = MainScreenView()
        wrap = QVBoxLayout(self)
        wrap.setContentsMargins(0, 0, 0, 0)
        wrap.addWidget(self.ui)

        self.setObjectName("main_screen")
        self.appshutdown.connect(self.ui.words_page.notified_app_shutting)
        self.appshutdown.connect(self.ui.sentences_page.notified_app_shutting)
        self.appshutdown.connect(self.ui.dictionary_page.notified_app_shutting)
        self.appshutdown.connect(self.ui.settings_page.notified_app_shutting)
        self.appshutdown.connect(self.ui.logs_page.notified_app_shutting)

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
