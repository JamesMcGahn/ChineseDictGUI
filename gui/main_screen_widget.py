from page_lessons import PageLessons
from page_words import PageWords
from PySide6.QtCore import QRect, QSize, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class MainScreenWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("main_screen_widget")
        with open("./gui/styles/main_screen_widget.css", "r") as ss:
            self.setStyleSheet(ss.read())
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_6 = QVBoxLayout(self)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(1, 1, 1, 1)
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName("stackedWidget")
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
        self.dictionary_page = QWidget()
        self.dictionary_page.setObjectName("dictionary_page")
        self.label_3 = QLabel(self.dictionary_page)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(480, 460, 221, 81))
        self.label_3.setFont(font1)
        self.label_3.setText("dictionary page")
        self.stackedWidget.addWidget(self.dictionary_page)
        self.settings_page = QWidget()
        self.settings_page.setObjectName("settings_page")
        self.label_5 = QLabel(self.settings_page)
        self.label_5.setObjectName("label_5")
        self.label_5.setGeometry(QRect(520, 430, 221, 81))
        self.label_5.setFont(font1)
        self.label_5.setText("settings page")
        self.stackedWidget.addWidget(self.settings_page)

        self.verticalLayout_6.addWidget(self.stackedWidget)

    @Slot(QPushButton)
    def change_page(self, btn):
        btn_name = btn.objectName()

        if btn_name.startswith("words_btn_"):
            self.stackedWidget.setCurrentIndex(0)
        elif btn_name.startswith("sents_btn_"):
            self.stackedWidget.setCurrentIndex(1)
        elif btn_name.startswith("audio_btn_"):
            self.stackedWidget.setCurrentIndex(2)
        elif btn_name.startswith("dictionary_btn_"):
            self.stackedWidget.setCurrentIndex(3)
        elif btn_name.startswith("settings_btn_"):
            self.stackedWidget.setCurrentIndex(4)
