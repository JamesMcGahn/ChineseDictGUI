from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class IconOnlyNavBarView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setObjectName("icon_only_widget_ui")

    def init_ui(self):
        self.setMaximumSize(QSize(70, 16777215))
        self.setMinimumSize(QSize(70, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.icon_nav_vlayout = QVBoxLayout(self)
        self.icon_nav_vlayout.setObjectName("icon_nav_vlayout")
        self.icon_btn_layout = QVBoxLayout()
        self.icon_btn_layout.setObjectName("icon_btn_layout_ico")
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

        self.icon_btn_layout.addWidget(self.words_btn_ico)

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

        self.icon_btn_layout.addWidget(self.sents_btn_ico)

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

        self.icon_btn_layout.addWidget(self.audio_btn_ico)

        self.dictionary_btn_ico = QPushButton()
        self.dictionary_btn_ico.setObjectName("dictionary_btn_ico")
        icon3 = QIcon()
        icon3.addFile(
            ":/ /images/dictionary_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon3.addFile(
            ":/ /images/dictionary_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.dictionary_btn_ico.setIcon(icon3)
        self.dictionary_btn_ico.setIconSize(QSize(100, 20))
        self.dictionary_btn_ico.setCheckable(True)
        self.dictionary_btn_ico.setAutoExclusive(True)

        self.icon_btn_layout.addWidget(self.dictionary_btn_ico)

        self.icon_nav_vlayout.addLayout(self.icon_btn_layout)

        self.verticalSpacer_2 = QSpacerItem(
            43, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.icon_nav_vlayout.addItem(self.verticalSpacer_2)

        self.settings_btn_ico = QPushButton()
        self.settings_btn_ico.setObjectName("settings_btn_ico")
        icon4 = QIcon()
        icon4.addFile(
            ":/ /images/settings_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon4.addFile(
            ":/ /images/settings_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.settings_btn_ico.setIcon(icon4)
        self.settings_btn_ico.setIconSize(QSize(100, 20))
        self.settings_btn_ico.setCheckable(True)
        self.settings_btn_ico.setAutoExclusive(True)

        self.icon_nav_vlayout.addWidget(self.settings_btn_ico)

        self.logs_btn_ico = QPushButton()
        self.logs_btn_ico.setObjectName("logs_btn_ico")
        icon6 = QIcon()
        icon6.addFile(
            ":/ /images/logs_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon6.addFile(
            ":/ /images/logs_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.logs_btn_ico.setIcon(icon6)
        self.logs_btn_ico.setIconSize(QSize(100, 20))
        self.logs_btn_ico.setCheckable(True)
        self.logs_btn_ico.setAutoExclusive(True)

        self.icon_nav_vlayout.addWidget(self.logs_btn_ico)

        self.signout_btn_ico = QPushButton()
        self.signout_btn_ico.setObjectName("signout_btn_ico")
        icon5 = QIcon()
        icon5.addFile(
            ":/ /images/signout_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon5.addFile(
            ":/ /images/signout_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.signout_btn_ico.setIcon(icon5)
        self.signout_btn_ico.setIconSize(QSize(100, 20))
        self.signout_btn_ico.setCheckable(True)
        self.signout_btn_ico.setAutoExclusive(True)

        self.icon_nav_vlayout.addWidget(self.signout_btn_ico)
