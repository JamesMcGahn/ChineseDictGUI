from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget

from page_settings import PageSettings
from views.pages import PageDictionary, PageLessons, PageWords


class MainScreenView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setObjectName("main_screen_ui")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QSize(16777215, 16777215))

        self.main_screen_container_v = QVBoxLayout(self)
        self.main_screen_container_v.setObjectName("main_screen_container_v")
        self.main_screen_container_v.setContentsMargins(1, 1, 1, 1)
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName("main_screen_stacked")
        self.words_page = PageWords()
        font1 = QFont()

        self.stackedWidget.addWidget(self.words_page)
        self.sentences_page = PageLessons()

        self.stackedWidget.addWidget(self.sentences_page)
        self.audio_page = QWidget()

        self.audio_page.setObjectName("audio_page")
        self.label_2 = QLabel(self.audio_page)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(350, 410, 221, 81))
        self.label_2.setFont(font1)
        self.label_2.setText("audio page")
        self.stackedWidget.addWidget(self.audio_page)

        self.dictionary_page = PageDictionary()

        self.stackedWidget.addWidget(self.dictionary_page)

        self.settings_page = PageSettings()

        self.stackedWidget.addWidget(self.settings_page)

        self.main_screen_container_v.addWidget(self.stackedWidget)
