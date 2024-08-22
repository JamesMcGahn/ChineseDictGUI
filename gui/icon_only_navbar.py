from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class IconOnlyNavBar(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("icon_only_widget")
        self.setMaximumSize(QSize(70, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)
        with open("./gui/styles/icon_only_navbar.css", "r") as ss:
            self.setStyleSheet(ss.read())

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.words_btn_ico = QPushButton()
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

        self.sents_btn_ico = QPushButton()
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

        self.audio_btn_ico = QPushButton()
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

        self.dictionary_ico = QPushButton()
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

        self.pushButton_8 = QPushButton()
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

        self.pushButton_9 = QPushButton()
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
