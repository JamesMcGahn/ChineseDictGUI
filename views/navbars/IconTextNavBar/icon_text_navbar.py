import os

from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QPushButton, QWidget

from .icon_text_navbar_ui import IconTextNavBarView


class IconTextNavBar(QWidget):
    btn_checked_ict = Signal(bool, QPushButton)
    btn_clicked_page = Signal(QPushButton)

    def __init__(self):
        super().__init__()

        self.setObjectName("icon_text_widget")
        self.setMaximumSize(QSize(250, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)

        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "icon_text_navbar.css")
        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())

        self.ui = IconTextNavBarView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.ui.words_btn_ict.toggled.connect(self.btn_checked)
        self.ui.sents_btn_ict.toggled.connect(self.btn_checked)
        self.ui.dictionary_btn_ict.toggled.connect(self.btn_checked)
        self.ui.audio_btn_ict.toggled.connect(self.btn_checked)
        self.ui.settings_btn_ict.toggled.connect(self.btn_checked)
        self.ui.logs_btn_ict.toggled.connect(self.btn_clicked)
        self.ui.signout_btn_ict.toggled.connect(self.btn_checked)

        self.ui.words_btn_ict.clicked.connect(self.btn_clicked)
        self.ui.sents_btn_ict.clicked.connect(self.btn_clicked)
        self.ui.dictionary_btn_ict.clicked.connect(self.btn_clicked)
        self.ui.audio_btn_ict.clicked.connect(self.btn_clicked)
        self.ui.settings_btn_ict.clicked.connect(self.btn_clicked)
        self.ui.logs_btn_ict.clicked.connect(self.btn_clicked)
        self.ui.signout_btn_ict.clicked.connect(self.btn_clicked)

        self.ui.words_btn_ict.setChecked(True)
        self.setHidden(True)

    def btn_checked(self, checked):
        self.btn_checked_ict.emit(checked, self.sender())

    def btn_clicked(self):
        self.btn_clicked_page.emit(self.sender())

    @Slot(bool)
    def hide_nav(self, checked):
        self.setHidden(not checked)

    @Slot(bool, QPushButton)
    def btns_set_checked(self, checked, btn):
        match btn.objectName():
            case "words_btn_ico":
                self.ui.words_btn_ict.setChecked(checked)
            case "sents_btn_ico":
                self.ui.sents_btn_ict.setChecked(checked)
            case "audio_btn_ico":
                self.ui.audio_btn_ict.setChecked(checked)
            case "dictionary_btn_ico":
                self.ui.dictionary_btn_ict.setChecked(checked)
            case "settings_btn_ico":
                self.ui.settings_btn_ict.setChecked(checked)
            case "logs_btn_ico":
                self.ui.logs_btn_ict.setChecked(checked)
            case "signout_btn_ico":
                self.ui.signout_btn_ict.setChecked(checked)
