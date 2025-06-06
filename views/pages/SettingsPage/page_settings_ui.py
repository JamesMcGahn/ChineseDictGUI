from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from components.utils import ColoredSpacer


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

        hspacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        vspacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # colored_spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.anki_deck_widget = QWidget()
        self.anki_deck_widget.setObjectName("anki_deck_widget")
        # self.anki_deck_widget.setMaximumSize(QSize(700, 200))
        self.anki_deck_widget.setMinimumSize(QSize(500, 200))
        # Anki Deck Layout
        self.anki_deck_vlayout = QVBoxLayout()
        self.anki_deck_vlayout.setSpacing(5)

        # Words Deck Labels
        self.label_anki_words_deck = QLabel("Word's Deck Name:")
        self.label_anki_words_deck.setMinimumWidth(143)
        self.lineEdit_anki_words_deck = QLineEdit()
        self.lineEdit_anki_words_deck.setMaximumWidth(230)
        self.label_anki_words_deck_verfied = QPushButton()
        self.label_anki_words_deck_verfied.setMinimumWidth(20)
        self.label_anki_words_deck_verfied.setObjectName("anki_verify_icon_w")
        self.x_icon = QIcon()
        self.x_icon.addFile(
            ":/ /images/red_check.png",
            QSize(),
            QIcon.Mode.Normal,
        )
        self.check_icon = QIcon()
        self.check_icon.addFile(
            ":/ /images/green_check.png",
            QSize(),
            QIcon.Mode.Normal,
        )

        self.label_anki_words_verify_btn = QPushButton("Verify Deck")

        self.anki_words_deck_hlayout = QHBoxLayout()
        self.anki_words_deck_hlayout.setSpacing(10)
        # self.anki_words_deck_hlayout.addItem(hspacer)
        self.anki_words_deck_hlayout.addWidget(self.label_anki_words_deck)
        self.anki_words_deck_hlayout.addWidget(self.lineEdit_anki_words_deck)
        self.anki_words_deck_hlayout.addWidget(self.label_anki_words_deck_verfied)
        self.anki_words_deck_hlayout.addWidget(self.label_anki_words_verify_btn)
        # self.anki_words_deck_hlayout.addItem(hspacer)

        # Sents Deck Labels
        self.label_anki_sents_deck = QLabel("Sentence's Deck Name:")
        self.label_anki_sents_deck.setMinimumWidth(143)
        self.lineEdit_anki_sents_deck = QLineEdit()
        self.lineEdit_anki_sents_deck.setMaximumWidth(230)
        self.label_anki_sents_deck_verfied = QPushButton()
        self.label_anki_sents_deck_verfied.setMinimumWidth(20)
        self.label_anki_sents_deck_verfied.setObjectName("anki_verify_icon_s")
        self.label_anki_sents_verify_btn = QPushButton("Verify Deck")

        self.anki_sents_deck_hlayout = QHBoxLayout()
        self.anki_sents_deck_hlayout.setSpacing(10)
        # self.anki_sents_deck_hlayout.addItem(hspacer)
        self.anki_sents_deck_hlayout.addWidget(self.label_anki_sents_deck)
        self.anki_sents_deck_hlayout.addWidget(self.lineEdit_anki_sents_deck)
        self.anki_sents_deck_hlayout.addWidget(self.label_anki_sents_deck_verfied)
        self.anki_sents_deck_hlayout.addWidget(self.label_anki_sents_verify_btn)
        # self.anki_sents_deck_hlayout.addItem(hspacer)

        # self.anki_deck_vlayout.addItem(vspacer)
        spacer1 = ColoredSpacer(
            "red", 400, 1, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        self.anki_deck_vlayout.addWidget(spacer1)
        self.anki_deck_vlayout.addLayout(self.anki_words_deck_hlayout)
        self.anki_deck_vlayout.addLayout(self.anki_sents_deck_hlayout)
        self.anki_deck_vlayout.addItem(vspacer)

        self.anki_deck_widget.setLayout(self.anki_deck_vlayout)

        self.settings_page_vlayout = QVBoxLayout(self)
        self.settings_page_vlayout.setSpacing(2)
        self.settings_page_vlayout.addWidget(self.label_6)
        anki_widget_hlayout = QHBoxLayout()
        anki_widget_hlayout.addItem(hspacer)
        anki_widget_hlayout.addWidget(self.anki_deck_widget)
        anki_widget_hlayout.addItem(hspacer)
        self.settings_page_vlayout.addLayout(anki_widget_hlayout)

        self.import_deck_btn = QPushButton("Import Deck From Anki")

        self.settings_page_vlayout.addWidget(self.import_deck_btn)

        self.sync_import_btn = QPushButton("Test Import Sync")

        self.settings_page_vlayout.addWidget(self.sync_import_btn)

        self.sync_export_btn = QPushButton("Test Export Sync")

        self.settings_page_vlayout.addWidget(self.sync_export_btn)
        self.settings_page_vlayout.addItem(vspacer)
