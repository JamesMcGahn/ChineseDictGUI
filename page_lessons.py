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

from components.dialogs import AddLessonsDialog, AddWordsDialog, IncreaseLvlsDialog
from lesson_scrape_thread import LessonScraperThread
from multiword_dialog import MultiWordDialog
from sents_table_model import SentenceTableModel
from word_scrape_thread import WordScraperThread
from word_table_model import WordTableModel


class PageLessons(QWidget):
    md_multi_selection_sig = Signal(int)
    use_cpod_def_sig = Signal(bool)
    updated_sents_levels_sig = Signal(bool, list)

    def __init__(self):
        super().__init__()
        self.setObjectName("lessons_page")
        with open("./styles/main_screen_widget.css", "r") as ss:
            self.setStyleSheet(ss.read())
        self.label_6 = QLabel()
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(280, 330, 221, 81))
        self.label_6.setText("Lessons page")
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
        self.words_table_vlayout = QVBoxLayout(self.words_table)
        self.table_wordmodel = WordTableModel()
        self.table_view = QTableView()
        self.table_view.setModel(self.table_wordmodel)
        self.table_view.show()
        self.words_table_vlayout.addWidget(self.table_view)
        self.stacked_widget.addWidget(self.words_table)

        # SentenceTable
        self.sents_table = QWidget()
        self.label = QLabel("dsd")
        self.sents_table_vlayout = QVBoxLayout(self.sents_table)
        self.table_sentmodel = SentenceTableModel()
        self.table_view = QTableView()
        self.table_view.setModel(self.table_sentmodel)
        self.table_view.show()
        self.sents_table_vlayout.addWidget(self.label)
        self.sents_table_vlayout.addWidget(self.table_view)
        self.stacked_widget.addWidget(self.sents_table)

        self.words_page_vlayout.addWidget(self.stacked_widget)
        self.dialog = AddLessonsDialog()

        self.stacked_widget.setCurrentIndex(1)
        self.addwords_btn.clicked.connect(self.addwords_btn_clicked)
        self.dialog.add_lesson_submited_signal.connect(self.get_dialog_submitted)
        self.words_table_btn.clicked.connect(self.change_table)
        self.sents_table_btn.clicked.connect(self.change_table)

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
        self.lesson_scrape_thread = LessonScraperThread(form_data)
        # TODO add list to the screen

        self.lesson_scrape_thread.start()
        self.lesson_scrape_thread.send_words_sig.connect(
            self.get_words_from_sthread_loop
        )
        self.lesson_scrape_thread.send_sents_sig.connect(
            self.get_sentences_from_thread_loop
        )

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
        print("page-word-received", words)
        if len(words) == 0:
            self.lesson_scrape_thread.deleteLater()
            return
        selection = "".join(f"{word.chinese}\n" for word in words)
        self.wdialog = AddWordsDialog(selection)
        self.wdialog.add_words_submited_signal.connect(self.get_wdialog_submitted)
        self.lesson_scrape_thread.deleteLater()
        # TODO Filter words out that arent already in db
        self.wdialog.exec()
        # self.table_wordmodel.add_word(word)

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
        print("received senteces", sentences)
        [self.table_sentmodel.add_sentence(x) for x in sentences]
