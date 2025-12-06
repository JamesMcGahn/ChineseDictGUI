import time

from PySide6.QtCore import Signal, Slot

from base import QWidgetBase
from components.toasts import QToast
from db import DatabaseManager, DatabaseQueryThread
from models.dictionary import Sentence, Word
from models.table import SentenceTableModel, WordTableModel
from services.audio import AudioThread

from .page_dictionary_ui import PageDictionaryView


class PageDictionary(QWidgetBase):
    md_multi_selection_sig = Signal(int)
    use_cpod_def_sig = Signal(bool)
    updated_sents_levels_sig = Signal(bool, list)

    def __init__(self):
        super().__init__()
        self.word_table_page = 1
        self.sent_table_page = 1
        self.audio_threads = []
        self.ui = PageDictionaryView()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.ui)

        self.setObjectName("dictionary_page")
        self.table_wordmodel = WordTableModel()
        self.table_sentmodel = SentenceTableModel()
        self.ui.table_view_w.setModel(self.table_wordmodel)
        self.ui.table_view_s.setModel(self.table_sentmodel)

        self.ui.words_table_btn.clicked.connect(self.change_table)
        self.ui.sents_table_btn.clicked.connect(self.change_table)

        self.ui.select_all_w.clicked.connect(self.select_all_words)
        self.ui.select_all_s.clicked.connect(self.select_all_sents)
        self.ui.delete_seled_w.clicked.connect(self.delete_selected_words)
        self.ui.delete_seled_s.clicked.connect(self.delete_selected_sents)
        self.ui.get_audio_w.clicked.connect(self.get_audio_for_selected_w)
        self.ui.get_audio_s.clicked.connect(self.get_audio_for_selected_s)

        self.ui.next_page_w.clicked.connect(self.words_nextpg_click)
        self.ui.prev_page_w.clicked.connect(self.words_prevpg_click)
        self.ui.next_page_s.clicked.connect(self.sents_nextpg_click)
        self.ui.prev_page_s.clicked.connect(self.sents_prevpg_click)

        self.dbw = DatabaseManager("chineseDict.db")
        self.dbs = DatabaseManager("chineseDict.db")

        self.table_wordmodel.wordUpdated.connect(self.word_updated)
        self.get_page_words(1, 20)
        self.get_page_sents(1, 20)

    def select_all_words(self):
        self.ui.table_view_w.selectAll()

    def select_all_sents(self):
        self.ui.table_view_s.selectAll()

    def get_audio_for_selected_w(
        self,
    ):
        selection_model = self.ui.table_view_w.selectionModel()
        selected_rows = selection_model.selectedRows()
        words = [
            self.table_wordmodel.get_row_data(index.row()) for index in selected_rows
        ]
        self.download_audio(words)

    def get_audio_for_selected_s(
        self,
    ):
        selection_model = self.ui.table_view_s.selectionModel()
        selected_rows = selection_model.selectedRows()
        words = [
            self.table_sentmodel.get_row_data(index.row()) for index in selected_rows
        ]
        self.download_audio(words)

    @Slot(list)
    def download_audio(self, audlist):
        # TODO get audio folder path from settings
        audio_thread = AudioThread(audlist, "./test/")

        audio_thread.updateAnkiAudio.connect(self.update_anki_audio)
        audio_thread.finished.connect(lambda: self.remove_thread(audio_thread))
        self.audio_threads.append(audio_thread)
        if len(self.audio_threads) == 1:
            audio_thread.start()

    def remove_thread(self, thread):
        if thread in self.audio_threads:
            print(f"removing thread {thread} from audio thread queue")
            self.audio_threads.remove(thread)
            thread.deleteLater()
        if self.audio_threads:
            self.audio_threads[0].start()

    @Slot(object)
    def update_anki_audio(self, obj):
        obj.local_update = int(time.time())

        if isinstance(obj, Sentence):
            self.upwThread = DatabaseQueryThread(
                "sents", "update_sentence", id=obj.id, updates=vars(obj)
            )
            self.upwThread.start()
            self.upwThread.finished.connect(self.upwThread.deleteLater)

        elif isinstance(obj, Word):
            self.upsThread = DatabaseQueryThread(
                "words", "update_word", id=obj.id, updates=vars(obj)
            )
            self.upsThread.start()
            self.upsThread.finished.connect(self.upsThread.deleteLater)

    # TODO Add Update Sentence
    @Slot(object)
    def word_updated(self, word):
        self.upwThread = DatabaseQueryThread(
            "words", "update_word", id=word.id, updates=vars(word)
        )
        self.upwThread.start()
        self.upwThread.message.connect(self.toast_message)

    def delete_selected_words(self):
        selection_model = self.ui.table_view_w.selectionModel()
        selected_rows = selection_model.selectedRows()
        words = [
            self.table_wordmodel.get_row_data(index.row()).id for index in selected_rows
        ]

        self.del_words = DatabaseQueryThread("words", "delete_words", ids=words)
        self.del_words.start()
        self.table_wordmodel.remove_selected(selected_rows)
        self.del_words.message.connect(self.toast_message)

    def delete_selected_sents(self):
        selection_model = self.ui.table_view_s.selectionModel()
        selected_rows = selection_model.selectedRows()
        sents = [
            self.table_sentmodel.get_row_data(index.row()).id for index in selected_rows
        ]

        self.del_sents = DatabaseQueryThread("sents", "delete_sentences", ids=sents)
        self.del_sents.start()
        self.table_sentmodel.remove_selected(selected_rows)
        self.del_sents.message.connect(self.toast_message)

    def change_table(self):
        btn_name = self.sender().objectName()

        if btn_name == "words_table_btn":
            self.ui.stacked_widget.setCurrentIndex(0)
        else:
            self.ui.stacked_widget.setCurrentIndex(1)

    def words_nextpg_click(self):
        self.get_page_words(self.word_table_page + 1, 20)
        self.word_table_page += 1

    def words_prevpg_click(self):
        if self.word_table_page > 1:
            self.get_page_words(self.word_table_page - 1, 20)
            self.word_table_page -= 1

    def sents_nextpg_click(self):
        self.get_page_sents(self.sent_table_page + 1, 20)
        self.sent_table_page += 1

    def sents_prevpg_click(self):
        if self.sent_table_page > 1:
            self.get_page_sents(self.sent_table_page - 1, 20)
            self.sent_table_page -= 1

    def get_page_words(self, page, limit):
        self.threader = DatabaseQueryThread(
            "words", "get_pagination_words", page=page, limit=limit
        )
        self.threader.start()
        self.threader.pagination.connect(self.load_words_page)

    def get_page_sents(self, page, limit):
        self.sthreader = DatabaseQueryThread(
            "sents", "get_pagination_sentences", page=page, limit=limit
        )
        self.sthreader.start()
        self.sthreader.pagination.connect(self.load_sents_page)

    @Slot(object, int, int, int, bool, bool)
    def load_words_page(
        self, words, table_count_result, total_pages, page, hasPrevPage, hasNextPage
    ):
        self.table_wordmodel.update_data(words)
        self.word_table_page = page

        if hasNextPage:
            self.ui.next_page_w.setDisabled(False)
        else:
            self.ui.next_page_w.setDisabled(True)

        if hasPrevPage:
            self.ui.prev_page_w.setDisabled(False)
        else:
            self.ui.prev_page_w.setDisabled(True)

    @Slot(object, int, int, int, bool, bool)
    def load_sents_page(
        self, sents, table_count_result, total_pages, page, hasPrevPage, hasNextPage
    ):
        self.table_sentmodel.update_data(sents)
        self.sent_table_page = page

        if hasNextPage:
            self.ui.next_page_s.setDisabled(False)
        else:
            self.ui.next_page_s.setDisabled(True)

        if hasPrevPage:
            self.ui.prev_page_s.setDisabled(False)
        else:
            self.ui.prev_page_s.setDisabled(True)

    @Slot(str)
    def toast_message(self, message):
        toast = QToast(self, status="success", title="Success!", message=message)
        toast.show()
