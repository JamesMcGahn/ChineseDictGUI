from PySide6.QtCore import QRect
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)


class PageDictionaryView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.label_6 = QLabel()
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(280, 330, 221, 81))
        self.label_6.setText("Dictionary")
        font1 = QFont()

        font1.setPointSize(25)
        self.label_6.setFont(font1)

        # TODO: Add Word Directly TO Dictionary
        # TODO: Add Sentence Directly to Dictionary
        self.add_btn = QPushButton("Add words")

        self.dictionary_page_vlayout = QVBoxLayout(self)

        self.dictionary_page_vlayout.addWidget(self.label_6)

        self.horizontal_btn_layout = QHBoxLayout()
        self.words_table_btn = QPushButton("Words")
        self.words_table_btn.setObjectName("words_table_btn")
        self.sents_table_btn = QPushButton("Sents")
        self.sents_table_btn.setObjectName("sents_table_btn")
        self.horizontal_btn_layout.addWidget(self.words_table_btn)
        self.horizontal_btn_layout.addWidget(self.sents_table_btn)

        self.dictionary_page_vlayout.addLayout(self.horizontal_btn_layout)
        # Stacked Widget
        self.stacked_widget = QStackedWidget()

        # WordsTable
        self.words_table = QWidget()

        self.select_all_w = QPushButton("Select All")
        self.delete_seled_w = QPushButton("Delete Selected")

        self.words_table_vlayout = QVBoxLayout(self.words_table)

        self.words_table_vlayout.addWidget(self.select_all_w)
        self.words_table_vlayout.addWidget(self.delete_seled_w)

        self.table_view_w = QTableView()
        self.table_view_w.setSelectionBehavior(QTableView.SelectRows)

        self.table_view_w.show()
        self.words_table_vlayout.addWidget(self.table_view_w)
        self.wnextbtns_hlayout = QHBoxLayout()
        self.next_page_w = QPushButton("Next Page")
        self.prev_page_w = QPushButton("Previous Page")
        self.wnextbtns_hlayout.addWidget(self.prev_page_w)
        self.wnextbtns_hlayout.addWidget(self.next_page_w)
        self.words_table_vlayout.addLayout(self.wnextbtns_hlayout)
        self.stacked_widget.addWidget(self.words_table)

        # SentenceTable
        self.sents_table = QWidget()

        self.select_all_s = QPushButton("Select All")
        self.delete_seled_s = QPushButton("Delete Selected")
        self.sents_table_vlayout = QVBoxLayout(self.sents_table)
        self.sents_table_vlayout.addWidget(self.select_all_s)
        self.sents_table_vlayout.addWidget(self.delete_seled_s)

        self.table_view_s = QTableView()
        self.table_view_s.setSelectionBehavior(QTableView.SelectRows)

        self.table_view_s.show()

        self.sents_table_vlayout.addWidget(self.table_view_s)
        self.snextbtns_hlayout = QHBoxLayout()
        self.next_page_s = QPushButton("Next Page")
        self.prev_page_s = QPushButton("Previous Page")
        self.snextbtns_hlayout.addWidget(self.prev_page_s)
        self.snextbtns_hlayout.addWidget(self.next_page_s)
        self.sents_table_vlayout.addLayout(self.snextbtns_hlayout)
        self.stacked_widget.addWidget(self.sents_table)

        self.stacked_widget.setCurrentIndex(0)
        self.dictionary_page_vlayout.addWidget(self.stacked_widget)
