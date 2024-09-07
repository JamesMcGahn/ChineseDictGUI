from PySide6.QtCore import QRect
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class PageSettingsUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setObjectName("settings_page_ui")
        self.label_6 = QLabel()
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(280, 330, 221, 81))
        self.label_6.setText("Settings page")
        font1 = QFont()

        font1.setPointSize(25)
        self.label_6.setFont(font1)

        self.settings_page_vlayout = QVBoxLayout(self)

        self.settings_page_vlayout.addWidget(self.label_6)

        self.import_deck_btn = QPushButton("Import Deck From Anki")

        self.settings_page_vlayout.addWidget(self.import_deck_btn)
