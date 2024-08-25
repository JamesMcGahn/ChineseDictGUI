from add_words_dialog import AddWordsDialog
from multiword_dialog import MultiWordDialog
from PySide6.QtCore import QRect, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from word_scrape_thread import WordScraperThread


class PageWords(QWidget):
    md_multi_selection_sig = Signal(int)
    use_cpod_def_sig = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setObjectName("words_page")
        with open("./gui/styles/main_screen_widget.css", "r") as ss:
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

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(
            ["Chinese", "Definition", "Pinyin", "Audio"]
        )
        self.words_page_vlayout.addWidget(self.table_widget)

        self.dialog = AddWordsDialog()

        self.addwords_btn.clicked.connect(self.addwords_btn_clicked)
        self.dialog.add_words_submited_signal.connect(self.get_dialog_submitted)

    def addwords_btn_clicked(self):
        self.dialog.exec()

    @Slot(dict)
    def get_dialog_submitted(self, form_data):
        print("slot", form_data)
        self.word_scrape_thread = WordScraperThread(
            form_data["word_list"],
            form_data["definition_source"],
            form_data["save_sentences"],
            form_data["level_selection"],
        )
        # TODO add list to the screen
        # TODO get thread started
        self.word_scrape_thread.start()
        self.word_scrape_thread.md_thd_multi_words_sig.connect(self.get_dialog_mdmulti)
        self.md_multi_selection_sig.connect(self.word_scrape_thread.get_md_user_select)
        self.use_cpod_def_sig.connect(self.word_scrape_thread.get_use_cpod_w)
        self.word_scrape_thread.send_word_sig.connect(self.get_word_from_thread_loop)
        self.word_scrape_thread.md_use_cpod_w_sig.connect(self.get_user_choice_usecpod)

    @Slot(list)
    def get_dialog_mdmulti(self, words):
        print("212121", words)
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
        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)
        self.table_widget.setItem(row, 0, QTableWidgetItem(word.chinese))
        self.table_widget.setItem(row, 1, QTableWidgetItem(word.definition))
        self.table_widget.setItem(row, 2, QTableWidgetItem(word.pinyin))
        self.table_widget.setItem(row, 3, QTableWidgetItem(word.audio))
