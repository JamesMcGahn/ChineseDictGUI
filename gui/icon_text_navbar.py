from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class IconTextNavBar(QWidget):
    btn_checked_ict = Signal(bool, QPushButton)

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
        self.icon_text_nav_vlayout = QVBoxLayout(self)
        self.icon_text_nav_vlayout.setObjectName("icon_text_nav_vlayout")
        self.icon_btn_layout = QVBoxLayout()
        self.icon_btn_layout.setObjectName("icon_btn_layout_ict")
        self.words_btn_ict = QPushButton(self)
        self.words_btn_ict.setObjectName("words_btn_ict")
        self.words_btn_ict.setIcon(icon)
        self.words_btn_ict.setIconSize(QSize(100, 20))
        self.words_btn_ict.setCheckable(True)
        self.words_btn_ict.setAutoExclusive(True)

        self.icon_btn_layout.addWidget(self.words_btn_ict)

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

        self.icon_btn_layout.addWidget(self.sents_btn_ict)

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

        self.icon_btn_layout.addWidget(self.audio_btn_ict)

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

        self.icon_btn_layout.addWidget(self.dictionary_btn_ict)

        self.icon_text_nav_vlayout.addLayout(self.icon_btn_layout)

        self.verticalSpacer_3 = QSpacerItem(
            20, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.icon_text_nav_vlayout.addItem(self.verticalSpacer_3)

        self.settings_btn_ict = QPushButton(self)
        self.settings_btn_ict.setObjectName("settings_btn_ict")
        self.settings_btn_ict.setIcon(icon4)
        self.settings_btn_ict.setIconSize(QSize(100, 20))
        self.settings_btn_ict.setCheckable(True)
        self.settings_btn_ict.setAutoExclusive(True)

        self.icon_text_nav_vlayout.addWidget(self.settings_btn_ict)

        self.signout_btn_ict = QPushButton(self)
        self.signout_btn_ict.setObjectName("signout_btn_ict")
        self.signout_btn_ict.setIcon(icon5)
        self.signout_btn_ict.setIconSize(QSize(100, 20))
        self.signout_btn_ict.setCheckable(True)
        self.signout_btn_ict.setAutoExclusive(True)
        self.words_btn_ict.setText(" Scrape Words")
        self.sents_btn_ict.setText(" Scrape Lessons")
        self.audio_btn_ict.setText(" Audio From File")
        self.dictionary_btn_ict.setText(" Dictionary")
        self.settings_btn_ict.setText("Settings")
        self.signout_btn_ict.setText("Exit")
        self.icon_text_nav_vlayout.addWidget(self.signout_btn_ict)
        self.setHidden(True)

        self.words_btn_ict.toggled.connect(self.btn_checked)
        self.sents_btn_ict.toggled.connect(self.btn_checked)
        self.dictionary_btn_ict.toggled.connect(self.btn_checked)
        self.audio_btn_ict.toggled.connect(self.btn_checked)
        self.settings_btn_ict.toggled.connect(self.btn_checked)
        self.signout_btn_ict.toggled.connect(self.btn_checked)

    def btn_checked(self, checked):
        self.btn_checked_ict.emit(checked, self.sender())

    @Slot(bool)
    def hide_nav(self, checked):
        self.setHidden(not checked)

    @Slot(bool, QPushButton)
    def btns_set_checked(self, checked, btn):
        match btn.objectName():
            case "words_btn_ico":
                self.words_btn_ict.setChecked(checked)
            case "sents_btn_ico":
                self.sents_btn_ict.setChecked(checked)
            case "audio_btn_ico":
                self.audio_btn_ict.setChecked(checked)
            case "dictionary_btn_ico":
                self.dictionary_btn_ict.setChecked(checked)
            case "settings_btn_ico":
                self.settings_btn_ict.setChecked(checked)
            case "signout_btn_ico":
                self.signout_btn_ict.setChecked(checked)
