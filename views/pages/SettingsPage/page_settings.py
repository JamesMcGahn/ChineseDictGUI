import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from components.toasts import QToast
from core.anki_integration.imports import AnkiInitialImportThread
from services.network import NetworkThread, SessionManager
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

        self.ui.label_anki_sents_verify_btn.clicked.connect(
            lambda checked, caller="sents": self.clicked_verify_deck_names(
                checked, caller
            )
        )
        self.ui.label_anki_words_verify_btn.clicked.connect(
            lambda checked, caller="words": self.clicked_verify_deck_names(
                checked, caller
            )
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
        self.ui.label_anki_sents_verify_btn.setDisabled(sents_verified)
        self.ui.label_anki_words_verify_btn.setDisabled(words_verified)

        self.settings.end_group()

    def change_deck_names(self, deckName, caller, verified=False):
        self.settings.begin_group("deckNames")
        self.settings.set_value(caller, deckName)
        self.settings.set_value(f"{caller}-verified", verified)
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

    def clicked_verify_deck_names(self, _, caller):
        print("sss", caller)
        sess = SessionManager()
        json = {"action": "deckNames", "version": 6}
        self.net_thread = NetworkThread(
            sess, "GET", "http://127.0.0.1:8765/", json=json
        )
        self.net_thread.response_sig.connect(
            lambda status, response, errorType=None, caller=caller: self.verify_decks_response(
                status, response, errorType, caller
            )
        )
        self.net_thread.start()

    def verify_decks_response(self, status, response, errorType, caller):
        response = response.json()
        if status == "success":
            deckName = self.settings.get_value(f"deckNames/{caller}", None)
            if deckName in response["result"]:
                self.change_deck_names(deckName, caller, True)
                QToast(
                    self,
                    "success",
                    "Deck Name Verified",
                    "Deck Name found in Anki, verify all decks and then start the integration!",
                ).show()
            else:
                QToast(
                    self,
                    "error",
                    "Deck Name Not Found",
                    "Deck Name not found in Anki, please make sure you have it typed correctly.",
                ).show()
