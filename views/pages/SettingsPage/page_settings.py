import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from core.anki_integration.imports import AnkiInitialImportThread
from services.settings import AppSettings

from .page_settings_ui import PageSettingsUI


class PageSettings(QWidget):
    md_multi_selection_sig = Signal(int)
    use_cpod_def_sig = Signal(bool)
    updated_sents_levels_sig = Signal(bool, list)

    def __init__(self):
        super().__init__()
        self.setObjectName("settings_page")
        module_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(module_dir, "settings.css")
        with open(file_path, "r") as ss:
            self.setStyleSheet(ss.read())
        self.ui = PageSettingsUI()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)
        self.settings = AppSettings()
        self.ui.import_deck_btn.clicked.connect(self.import_anki_deck)

        self.get_deck_names()

        self.ui.lineEdit_anki_sents_deck.textChanged.connect(
            lambda word, caller="sents": self.change_deck_names(word, caller)
        )
        self.ui.lineEdit_anki_words_deck.textChanged.connect(
            lambda word, caller="words": self.change_deck_names(word, caller)
        )

    def get_deck_names(self):
        self.settings.begin_group("deckNames")
        self.ui.lineEdit_anki_sents_deck.setText(self.settings.get_value("sents", ""))
        self.ui.lineEdit_anki_words_deck.setText(self.settings.get_value("words", ""))
        words_verified = self.settings.get_value("words-verified", False)
        sents_verified = self.settings.get_value("sents-verified", False)
        self.ui.label_anki_sents_deck_verfied.setText(
            f"{'OK' if sents_verified else 'X' }"
        )
        self.ui.label_anki_words_deck_verfied.setText(
            f"{'OK' if words_verified else 'X' }"
        )
        self.ui.label_anki_sents_verify_btn.setHidden(sents_verified)
        self.ui.label_anki_words_verify_btn.setHidden(words_verified)

        self.settings.end_group()

    def change_deck_names(self, word, caller):
        self.settings.begin_group("deckNames")
        self.settings.set_value(caller, word)
        self.settings.set_value(f"{caller}-verified", False)
        self.settings.end_group()
        self.get_deck_names()

    def import_anki_deck(self):
        self.import_anki_w = AnkiInitialImportThread("Mandarin Words", "words")
        self.import_anki_w.run()
        self.import_anki_w.finished.connect(self.import_anki_sents)

    # TODO: Refesh dictionary view when loaded
    # TODO: Remove threads
    def import_anki_sents(self):
        self.import_anki_s = AnkiInitialImportThread("Mandarin 10k Sentences", "sents")
        self.import_anki_s.run()
