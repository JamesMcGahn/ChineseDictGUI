import os

from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from .icon_only_navbar_ui import IconOnlyNavBarView


class IconOnlyNavBar(QWidget):
    btn_checked_ico = Signal(bool, QPushButton)
    btn_clicked_page = Signal(QPushButton)

    def __init__(self):
        super().__init__()
        self.setObjectName("icon_only_widget")
        self.setMaximumSize(QSize(70, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)

        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "icon_only_navbar.css")
        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())

        self.ui = IconOnlyNavBarView()
        wrap = QVBoxLayout(self)
        wrap.setContentsMargins(0, 0, 0, 0)
        wrap.addWidget(self.ui)

        self.ui.words_btn_ico.setChecked(True)

        self.ui.words_btn_ico.toggled.connect(self.btn_checked)
        self.ui.sents_btn_ico.toggled.connect(self.btn_checked)
        self.ui.dictionary_btn_ico.toggled.connect(self.btn_checked)
        self.ui.audio_btn_ico.toggled.connect(self.btn_checked)
        self.ui.settings_btn_ico.toggled.connect(self.btn_checked)
        self.ui.logs_btn_ico.toggled.connect(self.btn_checked)
        self.ui.signout_btn_ico.toggled.connect(self.btn_checked)

        self.ui.words_btn_ico.clicked.connect(self.btn_clicked)
        self.ui.sents_btn_ico.clicked.connect(self.btn_clicked)
        self.ui.dictionary_btn_ico.clicked.connect(self.btn_clicked)
        self.ui.audio_btn_ico.clicked.connect(self.btn_clicked)
        self.ui.settings_btn_ico.clicked.connect(self.btn_clicked)
        self.ui.logs_btn_ico.clicked.connect(self.btn_clicked)
        self.ui.signout_btn_ico.clicked.connect(self.btn_clicked)

    @Slot(bool)
    def hide_nav(self, checked):
        self.setHidden(checked)

    def btn_checked(self, checked):
        self.btn_checked_ico.emit(checked, self.sender())

    def btn_clicked(self):
        self.btn_clicked_page.emit(self.sender())

    @Slot(bool, QPushButton)
    def btns_set_checked(self, checked, btn):
        match btn.objectName():
            case "words_btn_ict":
                self.ui.words_btn_ico.setChecked(checked)
            case "sents_btn_ict":
                self.ui.sents_btn_ico.setChecked(checked)
            case "audio_btn_ict":
                self.ui.audio_btn_ico.setChecked(checked)
            case "dictionary_btn_ict":
                self.ui.dictionary_btn_ico.setChecked(checked)
            case "settings_btn_ict":
                self.ui.settings_btn_ico.setChecked(checked)
            case "logs_btn_ict":
                self.ui.logs_btn_ico.setChecked(checked)
            case "signout_btn_ict":
                self.ui.signout_btn_ico.setChecked(checked)
