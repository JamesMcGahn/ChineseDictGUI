# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'index.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1286, 962)
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setFamilies([".AppleSystemUIFont"])
        MainWindow.setFont(font)
        MainWindow.setStyleSheet("MainWindow{\n" "background-color: black;\n" "}")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.centralwidget.setStyleSheet(
            "QWidget#centralwidget {\n"
            "\n"
            "background-color: black;\n"
            "border: 1px solid red;\n"
            "border-bottom-left-radius: 9px;\n"
            "border-bottom-right-radius: 9px;\n"
            "}"
        )
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.main_screen_widget = QWidget(self.centralwidget)
        self.main_screen_widget.setObjectName("main_screen_widget")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.main_screen_widget.sizePolicy().hasHeightForWidth()
        )
        self.main_screen_widget.setSizePolicy(sizePolicy)
        self.main_screen_widget.setMaximumSize(QSize(16777215, 16777215))
        self.main_screen_widget.setStyleSheet(
            "QWidget#main_screen-widget {\n" "border: 1px solid red;\n" "}"
        )
        self.verticalLayout_6 = QVBoxLayout(self.main_screen_widget)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(1, 1, 1, 1)
        self.stackedWidget = QStackedWidget(self.main_screen_widget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.words_page = QWidget()
        self.words_page.setObjectName("words_page")
        self.label_6 = QLabel(self.words_page)
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(280, 330, 221, 81))
        font1 = QFont()
        font1.setPointSize(25)
        self.label_6.setFont(font1)
        self.stackedWidget.addWidget(self.words_page)
        self.sentences_page = QWidget()
        self.sentences_page.setObjectName("sentences_page")
        self.label_4 = QLabel(self.sentences_page)
        self.label_4.setObjectName("label_4")
        self.label_4.setGeometry(QRect(500, 370, 221, 81))
        self.label_4.setFont(font1)
        self.stackedWidget.addWidget(self.sentences_page)
        self.audio_page = QWidget()
        self.audio_page.setObjectName("audio_page")
        self.label_2 = QLabel(self.audio_page)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(350, 410, 221, 81))
        self.label_2.setFont(font1)
        self.stackedWidget.addWidget(self.audio_page)
        self.dictionary_page = QWidget()
        self.dictionary_page.setObjectName("dictionary_page")
        self.label_3 = QLabel(self.dictionary_page)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(480, 460, 221, 81))
        self.label_3.setFont(font1)
        self.stackedWidget.addWidget(self.dictionary_page)
        self.settings_page = QWidget()
        self.settings_page.setObjectName("settings_page")
        self.label_5 = QLabel(self.settings_page)
        self.label_5.setObjectName("label_5")
        self.label_5.setGeometry(QRect(520, 430, 221, 81))
        self.label_5.setFont(font1)
        self.stackedWidget.addWidget(self.settings_page)

        self.verticalLayout_6.addWidget(self.stackedWidget)

        self.gridLayout.addWidget(self.main_screen_widget, 2, 3, 1, 1)

        self.icon_only_widget = QWidget(self.centralwidget)
        self.icon_only_widget.setObjectName("icon_only_widget")
        self.icon_only_widget.setMaximumSize(QSize(70, 16777215))
        self.icon_only_widget.setStyleSheet(
            "QWidget#icon_only_widget{\n"
            "background-color: black;\n"
            "border: 1px solid red;\n"
            "border-bottom-left-radius: 9px;\n"
            "\n"
            "}\n"
            "\n"
            "\n"
            "\n"
            "\n"
            "QPushButton {\n"
            "border: none;\n"
            "background-color: black;\n"
            "padding: 1em .5em .5em .5em;\n"
            "\n"
            "color: white;\n"
            "}\n"
            "\n"
            "QPushButton:checked {\n"
            "border: none;\n"
            "background-color: white;\n"
            "border-radius:4px;\n"
            "height: 2em;\n"
            "color: black;\n"
            "}"
        )
        self.verticalLayout = QVBoxLayout(self.icon_only_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.words_btn_ico = QPushButton(self.icon_only_widget)
        self.words_btn_ico.setObjectName("words_btn_ico")
        icon = QIcon()
        icon.addFile(
            ":/ /images/list_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon.addFile(
            ":/ /images/list_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.words_btn_ico.setIcon(icon)
        self.words_btn_ico.setIconSize(QSize(100, 20))
        self.words_btn_ico.setCheckable(True)
        self.words_btn_ico.setAutoExclusive(True)

        self.verticalLayout_5.addWidget(self.words_btn_ico)

        self.sents_btn_ico = QPushButton(self.icon_only_widget)
        self.sents_btn_ico.setObjectName("sents_btn_ico")
        icon1 = QIcon()
        icon1.addFile(
            ":/ /images/dialogs_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon1.addFile(
            ":/ /images/dialogs_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.sents_btn_ico.setIcon(icon1)
        self.sents_btn_ico.setIconSize(QSize(100, 20))
        self.sents_btn_ico.setCheckable(True)
        self.sents_btn_ico.setAutoExclusive(True)

        self.verticalLayout_5.addWidget(self.sents_btn_ico)

        self.audio_btn_ico = QPushButton(self.icon_only_widget)
        self.audio_btn_ico.setObjectName("audio_btn_ico")
        icon2 = QIcon()
        icon2.addFile(
            ":/ /images/audio_file_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon2.addFile(
            ":/ /images/audio_file_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.audio_btn_ico.setIcon(icon2)
        self.audio_btn_ico.setIconSize(QSize(100, 20))
        self.audio_btn_ico.setCheckable(True)
        self.audio_btn_ico.setAutoExclusive(True)

        self.verticalLayout_5.addWidget(self.audio_btn_ico)

        self.dictionary_ico = QPushButton(self.icon_only_widget)
        self.dictionary_ico.setObjectName("dictionary_ico")
        icon3 = QIcon()
        icon3.addFile(
            ":/ /images/dictionary_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon3.addFile(
            ":/ /images/dictionary_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.dictionary_ico.setIcon(icon3)
        self.dictionary_ico.setIconSize(QSize(100, 20))
        self.dictionary_ico.setCheckable(True)
        self.dictionary_ico.setAutoExclusive(True)

        self.verticalLayout_5.addWidget(self.dictionary_ico)

        self.verticalLayout.addLayout(self.verticalLayout_5)

        self.verticalSpacer_2 = QSpacerItem(
            43, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.pushButton_8 = QPushButton(self.icon_only_widget)
        self.pushButton_8.setObjectName("pushButton_8")
        icon4 = QIcon()
        icon4.addFile(
            ":/ /images/settings_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon4.addFile(
            ":/ /images/settings_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.pushButton_8.setIcon(icon4)
        self.pushButton_8.setIconSize(QSize(100, 20))
        self.pushButton_8.setCheckable(True)
        self.pushButton_8.setAutoExclusive(True)

        self.verticalLayout.addWidget(self.pushButton_8)

        self.pushButton_9 = QPushButton(self.icon_only_widget)
        self.pushButton_9.setObjectName("pushButton_9")
        icon5 = QIcon()
        icon5.addFile(
            ":/ /images/signout_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon5.addFile(
            ":/ /images/signout_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.pushButton_9.setIcon(icon5)
        self.pushButton_9.setIconSize(QSize(100, 20))
        self.pushButton_9.setCheckable(True)
        self.pushButton_9.setAutoExclusive(True)

        self.verticalLayout.addWidget(self.pushButton_9)

        self.gridLayout.addWidget(self.icon_only_widget, 0, 1, 3, 1)

        self.icon_text_widget = QWidget(self.centralwidget)
        self.icon_text_widget.setObjectName("icon_text_widget")
        self.icon_text_widget.setMaximumSize(QSize(250, 16777215))
        self.icon_text_widget.setStyleSheet(
            "QWidget#icon_text_widget{\n"
            "background-color: black;\n"
            "border: 1px solid red;\n"
            "border-bottom-left-radius: 9px;\n"
            "padding: 2px;\n"
            "}\n"
            "\n"
            "QPushButton {\n"
            "border: none;\n"
            "background-color: black;\n"
            "padding: 1em .5em .5em .5em;\n"
            "text-align: left;\n"
            "color: white;\n"
            "\n"
            "}\n"
            "\n"
            "QPushButton:checked {\n"
            "background-color: white;\n"
            "border-radius: 4px;\n"
            "height: 2em;\n"
            "color: black;\n"
            "}"
        )
        self.verticalLayout_2 = QVBoxLayout(self.icon_text_widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.words_btn_ict = QPushButton(self.icon_text_widget)
        self.words_btn_ict.setObjectName("words_btn_ict")
        self.words_btn_ict.setIcon(icon)
        self.words_btn_ict.setIconSize(QSize(100, 20))
        self.words_btn_ict.setCheckable(True)
        self.words_btn_ict.setAutoExclusive(True)

        self.verticalLayout_4.addWidget(self.words_btn_ict)

        self.sents_btn_ict = QPushButton(self.icon_text_widget)
        self.sents_btn_ict.setObjectName("sents_btn_ict")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.sents_btn_ict.sizePolicy().hasHeightForWidth()
        )
        self.sents_btn_ict.setSizePolicy(sizePolicy1)
        self.sents_btn_ict.setMaximumSize(QSize(16777215, 16777215))
        self.sents_btn_ict.setIcon(icon1)
        self.sents_btn_ict.setIconSize(QSize(100, 20))
        self.sents_btn_ict.setCheckable(True)
        self.sents_btn_ict.setAutoExclusive(True)

        self.verticalLayout_4.addWidget(self.sents_btn_ict)

        self.audio_btn_ict = QPushButton(self.icon_text_widget)
        self.audio_btn_ict.setObjectName("audio_btn_ict")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.audio_btn_ict.sizePolicy().hasHeightForWidth()
        )
        self.audio_btn_ict.setSizePolicy(sizePolicy2)
        self.audio_btn_ict.setIcon(icon2)
        self.audio_btn_ict.setIconSize(QSize(100, 20))
        self.audio_btn_ict.setCheckable(True)
        self.audio_btn_ict.setAutoExclusive(True)

        self.verticalLayout_4.addWidget(self.audio_btn_ict)

        self.dictionary_btn_ict = QPushButton(self.icon_text_widget)
        self.dictionary_btn_ict.setObjectName("dictionary_btn_ict")
        sizePolicy1.setHeightForWidth(
            self.dictionary_btn_ict.sizePolicy().hasHeightForWidth()
        )
        self.dictionary_btn_ict.setSizePolicy(sizePolicy1)
        self.dictionary_btn_ict.setIcon(icon3)
        self.dictionary_btn_ict.setIconSize(QSize(100, 20))
        self.dictionary_btn_ict.setCheckable(True)
        self.dictionary_btn_ict.setAutoExclusive(True)

        self.verticalLayout_4.addWidget(self.dictionary_btn_ict)

        self.verticalLayout_2.addLayout(self.verticalLayout_4)

        self.verticalSpacer_3 = QSpacerItem(
            20, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.pushButton_10 = QPushButton(self.icon_text_widget)
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_10.setIcon(icon4)
        self.pushButton_10.setIconSize(QSize(100, 20))
        self.pushButton_10.setCheckable(True)
        self.pushButton_10.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.pushButton_10)

        self.pushButton_11 = QPushButton(self.icon_text_widget)
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_11.setIcon(icon5)
        self.pushButton_11.setIconSize(QSize(100, 20))
        self.pushButton_11.setCheckable(True)
        self.pushButton_11.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.pushButton_11)

        self.gridLayout.addWidget(self.icon_text_widget, 0, 2, 3, 1)

        self.header_widget = QWidget(self.centralwidget)
        self.header_widget.setObjectName("header_widget")
        self.header_widget.setMaximumSize(QSize(16777215, 175))
        self.header_widget.setStyleSheet(
            "QWidget#header_widget{\n"
            "background-color: rgb(0, 0, 0);\n"
            "border: 1px solid red;\n"
            "}"
        )
        self.verticalLayout_7 = QVBoxLayout(self.header_widget)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QLabel(self.header_widget)
        self.label.setObjectName("label")
        self.label.setStyleSheet("text-align: right;")
        self.label.setPixmap(QPixmap(":/ /images/logo.png"))

        self.verticalLayout_3.addWidget(self.label)

        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.horizontalSpacer_3 = QSpacerItem(
            558, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.lineEdit = QLineEdit(self.header_widget)
        self.lineEdit.setObjectName("lineEdit")
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QSize(250, 31))
        self.lineEdit.setMaximumSize(QSize(250, 31))
        self.lineEdit.setStyleSheet(
            "QLineEdit {\n"
            "	padding-left: 20px;\n"
            "	border: 1px solid gray;\n"
            "	border-radius: 10px;\n"
            "}"
        )

        self.horizontalLayout_2.addWidget(self.lineEdit)

        self.pushButton = QPushButton(self.header_widget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setStyleSheet(
            "QPushButton {\n" "border: none;\n" "padding-right:.5em\n" "}"
        )
        icon6 = QIcon()
        icon6.addFile(
            ":/ /images/hamburger_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon6.addFile(
            ":/ /images/hamburger_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.pushButton.setIcon(icon6)
        self.pushButton.setIconSize(QSize(29, 35))
        self.pushButton.setCheckable(True)

        self.horizontalLayout_2.addWidget(self.pushButton)

        self.verticalLayout_7.addLayout(self.horizontalLayout_2)

        self.gridLayout.addWidget(self.header_widget, 0, 3, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.words_btn_ico.toggled.connect(self.words_btn_ict.setChecked)
        self.words_btn_ict.toggled.connect(self.words_btn_ico.setChecked)
        self.sents_btn_ico.toggled.connect(self.sents_btn_ict.setChecked)
        self.sents_btn_ict.toggled.connect(self.sents_btn_ico.setChecked)
        self.audio_btn_ico.toggled.connect(self.audio_btn_ict.setChecked)
        self.audio_btn_ict.toggled.connect(self.audio_btn_ico.setChecked)
        self.dictionary_ico.toggled.connect(self.dictionary_btn_ict.setChecked)
        self.dictionary_btn_ict.toggled.connect(self.dictionary_ico.setChecked)
        self.pushButton_8.toggled.connect(self.pushButton_10.setChecked)
        self.pushButton_10.toggled.connect(self.pushButton_8.setChecked)
        self.pushButton_9.toggled.connect(self.pushButton_11.setChecked)
        self.pushButton_11.toggled.connect(self.pushButton_9.setChecked)
        self.pushButton.toggled.connect(self.icon_text_widget.setVisible)
        self.pushButton.toggled.connect(self.icon_only_widget.setHidden)

        self.stackedWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.label_6.setText(
            QCoreApplication.translate("MainWindow", "Words page", None)
        )
        self.label_4.setText(
            QCoreApplication.translate("MainWindow", "Sentences page", None)
        )
        self.label_2.setText(
            QCoreApplication.translate("MainWindow", "Audio page", None)
        )
        self.label_3.setText(
            QCoreApplication.translate("MainWindow", "Dictionary page", None)
        )
        self.label_5.setText(
            QCoreApplication.translate("MainWindow", "Settings page", None)
        )
        self.words_btn_ico.setText("")
        self.sents_btn_ico.setText("")
        self.audio_btn_ico.setText("")
        self.dictionary_ico.setText("")
        self.pushButton_8.setText("")
        self.pushButton_9.setText("")
        self.words_btn_ict.setText(
            QCoreApplication.translate("MainWindow", " Scrape Words", None)
        )
        self.sents_btn_ict.setText(
            QCoreApplication.translate("MainWindow", " Scrape Lessons", None)
        )
        self.audio_btn_ict.setText(
            QCoreApplication.translate("MainWindow", " Audio From File", None)
        )
        self.dictionary_btn_ict.setText(
            QCoreApplication.translate("MainWindow", " Dictionary", None)
        )
        self.pushButton_10.setText(
            QCoreApplication.translate("MainWindow", "Settings", None)
        )
        self.pushButton_11.setText(
            QCoreApplication.translate("MainWindow", "Exit", None)
        )
        self.label.setText("")
        self.lineEdit.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Search...", None)
        )
        self.pushButton.setText("")

    # retranslateUi
