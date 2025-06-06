import time

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QMessageBox, QWidget

from components.dialogs import (
    AddLessonsDialog,
    AddWordsDialog,
    IncreaseLvlsDialog,
    MultiWordDialog,
)
from core.scrapers.cpod.lessons import LessonScraperThread
from core.scrapers.words.word_scrape_thread import WordScraperThread
from db import DatabaseManager, DatabaseQueryThread
from models.dictionary import Sentence, Word
from models.table import SentenceTableModel, WordTableModel
from services.audio import AudioThread

from .page_lessons_ui import PageLessonsView


class PageLessons(QWidget):
    md_multi_selection_sig = Signal(int)
    use_cpod_def_sig = Signal(bool)
    updated_sents_levels_sig = Signal(bool, list)

    def __init__(self):
        super().__init__()
        self.ui = PageLessonsView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)
        self.audio_threads = []
        self.setObjectName("lessons_page")

        self.table_wordmodel = WordTableModel()
        self.table_sentmodel = SentenceTableModel()
        self.ui.table_view_s.setModel(self.table_sentmodel)
        self.ui.table_view_w.setModel(self.table_wordmodel)
        self.dialog = AddLessonsDialog()
        self.dialog.add_lesson_submited_signal.connect(self.get_dialog_submitted)
        self.dialog.add_lesson_closed.connect(self.add_word_dialog_closed)

        self.ui.stacked_widget.setCurrentIndex(1)
        self.ui.addwords_btn.clicked.connect(self.addwords_btn_clicked)

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
        for word in words:
            word.local_update = int(time.time())

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

    def save_selected_sents(self):
        selection_model = self.ui.table_view_s.selectionModel()
        selected_rows = selection_model.selectedRows()

        sents = []
        for index in selected_rows:
            save_sent = self.table_sentmodel.get_row_data(index.row())
            save_sent.local_update = int(time.time())
            sents.append(save_sent)

        print("aaaaa", sents)

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
        self.lesson_scrape_thread = LessonScraperThread(form_data)
        # TODO add list to the screen

        self.lesson_scrape_thread.start()
        self.lesson_scrape_thread.send_words_sig.connect(
            self.get_words_from_sthread_loop
        )
        self.lesson_scrape_thread.send_sents_sig.connect(
            self.get_sentences_from_thread_loop
        )
        self.lesson_scrape_thread.send_dialogue.connect(self.receive_dialogues)

    def receive_dialogues(self, lesson, dialogue):
        print("eeee", lesson, dialogue)
        print("eeee", vars(lesson), vars(dialogue))

        self.download_audio([lesson, dialogue])

    @Slot()
    def add_word_dialog_closed(self):
        self.lesson_scrape_thread.deleteLater()

    @Slot(list)
    def get_dialog_mdmulti(self, words):
        self.selectionDialog = MultiWordDialog(words)
        self.selectionDialog.md_multi_def_signal.connect(
            self.get_dialog_multi_selection
        )
        self.selectionDialog.exec()

    @Slot(int)
    def get_dialog_multi_selection(self, index):
        self.md_multi_selection_sig.emit(index)

    @Slot(object)
    def get_user_choice_usecpod(self, word):
        print("herer")
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
    def get_words_from_sthread_loop(self, words):
        print("page-word-received", len(words))
        if len(words) == 0:
            return
        else:
            # dup_check = "".join(f"{word.chinese}" for word in words)
            self.check_word_duplicates = DatabaseQueryThread(
                "words", "check_for_duplicate_words", words=words
            )
            self.check_word_duplicates.start()
            self.check_word_duplicates.result.connect(
                lambda result: self.receive_duplicates(result, words)
            )
            self.check_word_duplicates.finished.connect(
                self.check_word_duplicates.deleteLater
            )

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

    @Slot(object)
    def get_word_from_thread_loop(self, word):
        print("page-word-received", word)

        self.table_wordmodel.add_word(word)

    @Slot(object)
    def get_wdialog_submitted(self, form_data):
        self.word_scrape_thread = WordScraperThread(
            form_data["word_list"],
            form_data["definition_source"],
            form_data["save_sentences"],
            form_data["level_selection"],
        )
        # TODO add list to the screen

        self.word_scrape_thread.start()
        self.word_scrape_thread.md_thd_multi_words_sig.connect(self.get_dialog_mdmulti)
        self.md_multi_selection_sig.connect(self.word_scrape_thread.get_md_user_select)
        self.use_cpod_def_sig.connect(self.word_scrape_thread.get_use_cpod_w)
        self.word_scrape_thread.send_word_sig.connect(self.get_word_from_thread_loop)
        self.word_scrape_thread.md_use_cpod_w_sig.connect(self.get_user_choice_usecpod)
        self.word_scrape_thread.no_sents_inc_levels.connect(
            self.get_user_no_sents_inclvl
        )

        self.updated_sents_levels_sig.connect(
            self.word_scrape_thread.get_updated_sents_levels
        )
        self.word_scrape_thread.send_sents_sig.connect(
            self.get_sentences_from_thread_loop
        )
        self.word_scrape_thread.finished.connect(self.word_scrape_thread.deleteLater)

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
        print("received senteces", len(sentences))

        self.check_sentences_duplicates = DatabaseQueryThread(
            "sents", "check_for_duplicate_sentences", sentences=sentences
        )
        self.check_sentences_duplicates.start()
        self.check_sentences_duplicates.result.connect(
            lambda result: self.receive_duplicate_sentences(result, sentences)
        )
        self.check_sentences_duplicates.finished.connect(
            self.check_sentences_duplicates.deleteLater
        )

    def receive_duplicate_sentences(self, result, sentences):
        unique_sentences = [
            sentence for sentence in sentences if sentence.chinese not in result
        ]
        already_in_db_sentences = [
            sentence for sentence in sentences if sentence.chinese in result
        ]
        print("sentences already in db", already_in_db_sentences)
        # unique_words = "".join(f"{word.chinese}\n" for word in words)

        if len(unique_sentences) == 0:
            print("No words to add")
        else:
            # self.wdialog = AddWordsDialog(unique_words)
            # self.wdialog.add_words_submited_signal.connect(self.get_wdialog_submitted)

            # TODO Filter words out that arent already in db
            # self.wdialog.exec()

            [self.table_sentmodel.add_sentence(x) for x in unique_sentences]
