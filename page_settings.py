from PySide6.QtCore import QRect, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from anki_import_thread import AnkiImportThread
from lesson_scrape_thread import LessonScraperThread
from sents_table_model import SentenceTableModel
from word_scrape_thread import WordScraperThread
from word_table_model import WordTableModel


class PageSettings(QWidget):
    md_multi_selection_sig = Signal(int)
    use_cpod_def_sig = Signal(bool)
    updated_sents_levels_sig = Signal(bool, list)

    def __init__(self):
        super().__init__()
        self.setObjectName("settings_page")
        with open("./styles/main_screen_widget.css", "r") as ss:
            self.setStyleSheet(ss.read())
        self.label_6 = QLabel()
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(280, 330, 221, 81))
        self.label_6.setText("Settings page")
        font1 = QFont()

        font1.setPointSize(25)
        self.label_6.setFont(font1)

        self.addwords_btn = QPushButton("Add words")

        self.words_page_vlayout = QVBoxLayout(self)
        self.words_page_vlayout.addWidget(self.addwords_btn)
        self.words_page_vlayout.addWidget(self.label_6)

        self.horizontal_btn_layout = QHBoxLayout()
        self.words_table_btn = QPushButton("Words")
        self.words_table_btn.setObjectName("words_table_btn")
        self.sents_table_btn = QPushButton("Sents")
        self.sents_table_btn.setObjectName("sents_table_btn")
        self.horizontal_btn_layout.addWidget(self.words_table_btn)
        self.horizontal_btn_layout.addWidget(self.sents_table_btn)

        self.words_page_vlayout.addLayout(self.horizontal_btn_layout)

        self.import_deck_btn = QPushButton("Import Deck From Anki")

        self.words_page_vlayout.addWidget(self.import_deck_btn)

        self.import_deck_btn.clicked.connect(self.import_anki_deck)

    def import_anki_deck(self):
        self.import_anki_w = AnkiImportThread("Mandarin Words", "words")
        self.import_anki_w.run()
        self.import_anki_w.finished.connect(self.import_anki_sents)

    def import_anki_sents(self):
        self.import_anki_s = AnkiImportThread("Mandarin 10k Sentences", "sents")
        self.import_anki_s.run()
