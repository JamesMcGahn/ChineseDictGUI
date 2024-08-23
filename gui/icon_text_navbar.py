from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class IconTextNavBar(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("icon_text_widget")
        self.setMaximumSize(QSize(250, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)
        with open("./gui/styles/icon_text_navbar.css", "r") as ss:
            self.setStyleSheet(ss.read())
        icon = QIcon()
        icon.addFile(
            ":/ /images/list_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon.addFile(
            ":/ /images/list_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        icon1 = QIcon()
        icon1.addFile(
            ":/ /images/dialogs_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon1.addFile(
            ":/ /images/dialogs_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        icon2 = QIcon()
        icon2.addFile(
            ":/ /images/audio_file_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon2.addFile(
            ":/ /images/audio_file_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        icon3 = QIcon()
        icon3.addFile(
            ":/ /images/dictionary_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon3.addFile(
            ":/ /images/dictionary_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        icon4 = QIcon()
        icon4.addFile(
            ":/ /images/settings_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon4.addFile(
            ":/ /images/settings_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        icon5 = QIcon()
        icon5.addFile(
            ":/ /images/signout_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon5.addFile(
            ":/ /images/signout_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.verticalLayout_2 = QVBoxLayout(self)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.words_btn_ict = QPushButton(self)
        self.words_btn_ict.setObjectName("words_btn_ict")
        self.words_btn_ict.setIcon(icon)
        self.words_btn_ict.setIconSize(QSize(100, 20))
        self.words_btn_ict.setCheckable(True)
        self.words_btn_ict.setAutoExclusive(True)

        self.verticalLayout_4.addWidget(self.words_btn_ict)

        self.sents_btn_ict = QPushButton(self)
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

        self.audio_btn_ict = QPushButton(self)
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

        self.dictionary_btn_ict = QPushButton(self)
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

        self.pushButton_10 = QPushButton(self)
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_10.setIcon(icon4)
        self.pushButton_10.setIconSize(QSize(100, 20))
        self.pushButton_10.setCheckable(True)
        self.pushButton_10.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.pushButton_10)

        self.pushButton_11 = QPushButton(self)
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_11.setIcon(icon5)
        self.pushButton_11.setIconSize(QSize(100, 20))
        self.pushButton_11.setCheckable(True)
        self.pushButton_11.setAutoExclusive(True)
        self.words_btn_ict.setText(" Scrape Words")
        self.sents_btn_ict.setText(" Scrape Lessons")
        self.audio_btn_ict.setText(" Audio From File")
        self.dictionary_btn_ict.setText(" Dictionary")
        self.pushButton_10.setText("Settings")
        self.pushButton_11.setText("Exit")
        self.verticalLayout_2.addWidget(self.pushButton_11)
        self.setHidden(True)

    @Slot(bool)
    def hide_nav(self, bool):
        self.setHidden(not bool)
