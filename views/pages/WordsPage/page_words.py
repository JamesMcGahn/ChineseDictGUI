from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtWidgets import QMessageBox, QWidget

from components.dialogs import AddWordsDialog, IncreaseLvlsDialog, MultiWordDialog
from core.scrapers.words import WordScraperThreadV2
from db import DatabaseManager, DatabaseQueryThread
from models.dictionary import Sentence
from models.table import SentenceTableModel, WordTableModel
from services.audio import AudioThread

from .page_words_ui import PageWordsView


# TODO: Clean up
class PageWords(QWidget):
    md_multi_selection_sig = Signal(int)
    use_cpod_def_sig = Signal(bool)
    updated_sents_levels_sig = Signal(bool, list)

    def __init__(self):
        super().__init__()
        self.ui = PageWordsView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)
        self.audio_threads = []

        self.table_wordmodel = WordTableModel()
        self.table_sentmodel = SentenceTableModel()
        self.ui.table_view_w.setModel(self.table_wordmodel)
        self.ui.table_view_s.setModel(self.table_sentmodel)

        self.dialog = AddWordsDialog()

        self.ui.stacked_widget.setCurrentIndex(0)
        self.ui.addwords_btn.clicked.connect(self.addwords_btn_clicked)
        self.dialog.add_words_submited_signal.connect(self.get_dialog_submitted)
        self.ui.words_table_btn.clicked.connect(self.change_table)
        self.ui.sents_table_btn.clicked.connect(self.change_table)
        self.ui.save_btn_words.clicked.connect(self.save_selected_words)
        self.ui.save_btn_sents.clicked.connect(self.save_selected_sents)
        self.ui.select_all_w.clicked.connect(self.select_all_words)
        self.ui.select_all_s.clicked.connect(self.select_all_sents)

        self.dbw = DatabaseManager("chineseDict.db")
        self.dbs = DatabaseManager("chineseDict.db")

    def select_all_words(self):
        self.ui.table_view_w.selectAll()

    def select_all_sents(self):
        self.ui.table_view_s.selectAll()

    def save_selected_words(self):
        selection_model = self.ui.table_view_w.selectionModel()
        selected_rows = selection_model.selectedRows()
        words = [
            self.table_wordmodel.get_row_data(index.row()) for index in selected_rows
        ]
        self.save_selwords = DatabaseQueryThread("words", "insert_words", words=words)
        self.save_selwords.start()
        self.table_wordmodel.remove_selected(selected_rows)
        self.save_selwords.result.connect(self.download_audio)

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
        if isinstance(obj, Sentence):
            self.upwThread = DatabaseQueryThread(
                "sents", "update_sentence", id=obj.id, updates=vars(obj)
            )
            self.upwThread.start()
            self.upwThread.finished.connect(self.upwThread.deleteLater)

        else:
            self.upsThread = DatabaseQueryThread(
                "words", "update_word", id=obj.id, updates=vars(obj)
            )
            self.upsThread.start()
            self.upsThread.finished.connect(self.upsThread.deleteLater)

    def save_selected_sents(self):
        selection_model = self.ui.table_view_s.selectionModel()
        selected_rows = selection_model.selectedRows()
        sents = [
            self.table_sentmodel.get_row_data(index.row()) for index in selected_rows
        ]
        self.save_selsents = DatabaseQueryThread(
            "sents", "insert_sentences", sentences=sents
        )
        self.save_selsents.start()
        self.table_sentmodel.remove_selected(selected_rows)
        self.save_selsents.result.connect(self.download_audio)
        self.save_selsents.finished.connect(self.save_selsents.deleteLater)

    def change_table(self):
        btn_name = self.sender().objectName()

        if btn_name == "words_table_btn":
            self.ui.stacked_widget.setCurrentIndex(0)
        else:
            self.ui.stacked_widget.setCurrentIndex(1)

    def addwords_btn_clicked(self):
        self.dialog.exec()

    @Slot(dict)
    def get_dialog_submitted(self, form_data):
        print("here recieved submitted")
        self.word_scrape_thread = QThread()
        self.word_scrape_worker = WordScraperThreadV2(
            form_data["word_list"],
            form_data["definition_source"],
            form_data["save_sentences"],
            form_data["level_selection"],
        )
        # TODO add list to the screen
        self.word_scrape_worker.moveToThread(self.word_scrape_thread)
        self.word_scrape_thread.started.connect(self.word_scrape_worker.do_work)

        self.ui.addwords_btn.setDisabled(True)
        self.word_scrape_worker.md_thd_multi_words_sig.connect(self.get_dialog_mdmulti)
        self.md_multi_selection_sig.connect(self.word_scrape_worker.get_md_user_select)
        self.use_cpod_def_sig.connect(self.word_scrape_worker.get_use_cpod_w)
        self.word_scrape_worker.send_word_sig.connect(self.get_word_from_thread_loop)
        self.word_scrape_worker.md_use_cpod_w_sig.connect(self.get_user_choice_usecpod)
        self.word_scrape_worker.no_sents_inc_levels.connect(
            self.get_user_no_sents_inclvl
        )

        self.updated_sents_levels_sig.connect(
            self.word_scrape_worker.get_updated_sents_levels
        )
        self.word_scrape_worker.send_sents_sig.connect(
            self.get_sentences_from_thread_loop
        )

        self.word_scrape_worker.finished.connect(self.word_scrape_worker.deleteLater)
        self.word_scrape_worker.finished.connect(self.word_scrape_thread.quit)
        self.word_scrape_thread.finished.connect(self.thread_finished)
        self.word_scrape_thread.start()

    @Slot(list)
    def get_dialog_mdmulti(self, words):
        self.selectionDialog = MultiWordDialog(words)
        self.selectionDialog.md_multi_def_signal.connect(
            self.get_dialog_multi_selection
        )
        self.selectionDialog.exec()

    @Slot(int)
    def get_dialog_multi_selection(self, index):
        print(index, "selection", type(index))
        self.md_multi_selection_sig.emit(index)

    @Slot(object)
    def get_user_choice_usecpod(self, word):
        ret = QMessageBox.question(
            self,
            "No MDBG definition available.",
            f"No MDBG definition available.\n Use Cpod's definition?: \n {word.chinese} - {word.definition}",
            QMessageBox.Ok | QMessageBox.Cancel,
        )
        if ret == QMessageBox.Ok:
            self.use_cpod_def_sig.emit(True)
        else:
            self.use_cpod_def_sig.emit(False)

    @Slot(object)
    def get_word_from_thread_loop(self, word):
        print("page-word-received", word)

        self.check_word_duplicates = DatabaseQueryThread(
            "words", "check_for_duplicate_words", words=[word]
        )
        self.check_word_duplicates.start()
        self.check_word_duplicates.result.connect(
            lambda result: self.receive_duplicates(result, [word])
        )
        self.check_word_duplicates.finished.connect(
            self.check_word_duplicates.deleteLater
        )

        # self.table_wordmodel.add_word(word)

    def receive_duplicates(self, result, words):
        unique_words = [word for word in words if word.chinese not in result]
        already_in_db_words = [word for word in words if word.chinese in result]
        print("words already in db", already_in_db_words)
        # unique_words = "".join(f"{word.chinese}\n" for word in words)

        if len(unique_words) == 0:
            print("No words to add")
        else:
            # self.wdialog = AddWordsDialog(unique_words)
            # self.wdialog.add_words_submited_signal.connect(self.get_wdialog_submitted)

            # TODO Filter words out that arent already in db
            # self.wdialog.exec()
            [self.table_wordmodel.add_word(x) for x in unique_words]

    @Slot(list)
    def get_user_no_sents_inclvl(self, levels):
        self.nosentsDialog = IncreaseLvlsDialog(levels)
        self.nosentsDialog.sent_lvls_change_sig.connect(
            self.user_no_sents_inclvl_selection
        )
        self.nosentsDialog.exec()

    @Slot(bool, list)
    def user_no_sents_inclvl_selection(self, changed, levels):
        if changed:
            self.updated_sents_levels_sig.emit(changed, levels)
        else:
            self.updated_sents_levels_sig.emit(False, levels)

    @Slot(list)
    def get_sentences_from_thread_loop(self, sentences):
        print("received senteces", sentences)
        [self.table_sentmodel.add_sentence(x) for x in sentences]

    @Slot()
    def thread_finished(self):
        self.ui.addwords_btn.setDisabled(False)
