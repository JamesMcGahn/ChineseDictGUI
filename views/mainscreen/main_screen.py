from PySide6.QtCore import Slot
from PySide6.QtWidgets import QPushButton, QWidget

from .main_screen_ui import MainScreenView


class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = MainScreenView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.setObjectName("main_screen")

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
