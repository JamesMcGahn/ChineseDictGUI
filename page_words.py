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

from audio_thread import AudioThread
from components.dialogs import AddWordsDialog, IncreaseLvlsDialog
from db_manager import DatabaseManager
from db_query_thread import DatabaseQueryThread
from dictionary import Sentence
from multiword_dialog import MultiWordDialog
from sents_table_model import SentenceTableModel
from word_scrape_thread import WordScraperThread
from word_table_model import WordTableModel


class PageWords(QWidget):
    md_multi_selection_sig = Signal(int)
    use_cpod_def_sig = Signal(bool)
    updated_sents_levels_sig = Signal(bool, list)

    def __init__(self):
        super().__init__()

        self.audio_threads = []

        self.setObjectName("words_page")
        with open("./styles/main_screen_widget.css", "r") as ss:
            self.setStyleSheet(ss.read())
        self.label_6 = QLabel()
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(280, 330, 221, 81))
        self.label_6.setText("words page")
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
        # Stacked Widget
        self.stacked_widget = QStackedWidget()

        # WordsTable
        self.words_table = QWidget()
        self.save_btn_words = QPushButton("Save Selected")
        self.select_all_w = QPushButton("Select All")
        self.words_table_vlayout = QVBoxLayout(self.words_table)
        self.words_table_vlayout.addWidget(self.save_btn_words)
        self.words_table_vlayout.addWidget(self.select_all_w)
        self.table_wordmodel = WordTableModel()
        self.table_view_w = QTableView()
        self.table_view_w.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_w.setModel(self.table_wordmodel)
        self.table_view_w.show()
        self.words_table_vlayout.addWidget(self.table_view_w)
        self.stacked_widget.addWidget(self.words_table)

        # SentenceTable
        self.sents_table = QWidget()
        self.label = QLabel("dsd")
        self.save_btn_sents = QPushButton("Save Selected")
        self.select_all_s = QPushButton("Select All")

        self.sents_table_vlayout = QVBoxLayout(self.sents_table)
        self.sents_table_vlayout.addWidget(self.save_btn_sents)
        self.sents_table_vlayout.addWidget(self.select_all_s)
        self.table_sentmodel = SentenceTableModel()
        self.table_view_s = QTableView()
        self.table_view_s.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_s.setModel(self.table_sentmodel)
        self.table_view_s.show()
        self.sents_table_vlayout.addWidget(self.label)
        self.sents_table_vlayout.addWidget(self.table_view_s)
        self.stacked_widget.addWidget(self.sents_table)

        self.words_page_vlayout.addWidget(self.stacked_widget)
        self.dialog = AddWordsDialog()

        self.stacked_widget.setCurrentIndex(0)
        self.addwords_btn.clicked.connect(self.addwords_btn_clicked)
        self.dialog.add_words_submited_signal.connect(self.get_dialog_submitted)
        self.words_table_btn.clicked.connect(self.change_table)
        self.sents_table_btn.clicked.connect(self.change_table)
        self.save_btn_words.clicked.connect(self.save_selected_words)
        self.save_btn_sents.clicked.connect(self.save_selected_sents)
        self.select_all_w.clicked.connect(self.select_all_words)
        self.select_all_s.clicked.connect(self.select_all_sents)

        self.dbw = DatabaseManager("chineseDict.db")
        self.dbs = DatabaseManager("chineseDict.db")

    def select_all_words(self):
        self.table_view_w.selectAll()

    def select_all_sents(self):
        self.table_view_s.selectAll()

    def save_selected_words(self):
        selection_model = self.table_view_w.selectionModel()
        selected_rows = selection_model.selectedRows()
        words = [
            self.table_wordmodel.get_row_data(index.row()) for index in selected_rows
        ]
        self.save_selwords = DatabaseQueryThread(self.dbw, "insert_words", words=words)
        self.save_selwords.start()
        self.table_wordmodel.remove_selected(selected_rows)
        self.save_selwords.insertIds.connect(self.download_audio)

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
        thread.deleteLater()
        self.audio_threads.remove(thread)
        if self.audio_threads:
            self.audio_threads[0].start()

    @Slot(object)
    def update_anki_audio(self, obj):
        if isinstance(obj, Sentence):
            self.upwThread = DatabaseQueryThread(
                self.dbw, "update_sentence", id=obj.id, updates=vars(obj)
            )
            self.upwThread.start()
            self.upwThread.finished.connect(self.upwThread.deleteLater)

        else:
            self.upsThread = DatabaseQueryThread(
                self.dbs, "update_word", id=obj.id, updates=vars(obj)
            )
            self.upsThread.start()
            self.upsThread.finished.connect(self.upsThread.deleteLater)

    def save_selected_sents(self):
        selection_model = self.table_view_s.selectionModel()
        selected_rows = selection_model.selectedRows()
        sents = [
            self.table_sentmodel.get_row_data(index.row()) for index in selected_rows
        ]
        self.save_selsents = DatabaseQueryThread(
            self.dbs, "insert_sentences", sentences=sents
        )
        self.save_selsents.start()
        self.table_sentmodel.remove_selected(selected_rows)
        self.save_selsents.insertIds.connect(self.download_audio)
        self.save_selsents.finished.connect(self.save_selsents.deleteLater)

    def change_table(self):
        btn_name = self.sender().objectName()

        if btn_name == "words_table_btn":
            self.stacked_widget.setCurrentIndex(0)
        else:
            self.stacked_widget.setCurrentIndex(1)

    def addwords_btn_clicked(self):
        self.dialog.exec()

    @Slot(dict)
    def get_dialog_submitted(self, form_data):
        self.word_scrape_thread = WordScraperThread(
            form_data["word_list"],
            form_data["definition_source"],
            form_data["save_sentences"],
            form_data["level_selection"],
        )
        # TODO add list to the screen
        # TODO disable the add words button when starting thread
        self.addwords_btn.setDisabled(True)
        self.word_scrape_thread.start()
        self.word_scrape_thread.finished.connect(self.word_scrape_thread.deleteLater)
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
        self.word_scrape_thread.thread_finished.connect(self.thread_finished)

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
    def get_word_from_thread_loop(self, word):
        print("page-word-received", word)

        self.table_wordmodel.add_word(word)

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

    @Slot(bool)
    def thread_finished(self, isFinished):
        if isFinished:
            self.addwords_btn.setDisabled(False)
