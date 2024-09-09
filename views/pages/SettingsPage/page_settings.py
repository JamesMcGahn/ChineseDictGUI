from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from anki_import_thread import AnkiImportThread

from .page_settings_ui import PageSettingsUI


class PageSettings(QWidget):
    md_multi_selection_sig = Signal(int)
    use_cpod_def_sig = Signal(bool)
    updated_sents_levels_sig = Signal(bool, list)

    def __init__(self):
        super().__init__()
        self.setObjectName("settings_page")

        self.ui = PageSettingsUI()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.ui.import_deck_btn.clicked.connect(self.import_anki_deck)

    def import_anki_deck(self):
        self.import_anki_w = AnkiImportThread("Mandarin Words", "words")
        self.import_anki_w.run()
        self.import_anki_w.finished.connect(self.import_anki_sents)

    # TODO: Refesh dictionary view when loaded
    def import_anki_sents(self):
        self.import_anki_s = AnkiImportThread("Mandarin 10k Sentences", "sents")
        self.import_anki_s.run()
