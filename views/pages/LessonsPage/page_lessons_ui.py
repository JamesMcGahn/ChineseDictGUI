from PySide6.QtCore import QRect, Slot
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


class PageLessonsView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setObjectName("lessons_page")
        self.label_6 = QLabel()
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(280, 330, 221, 81))
        self.label_6.setText("Lessons page")
        font1 = QFont()

        font1.setPointSize(25)
        self.label_6.setFont(font1)

        self.addwords_btn = QPushButton("Add Lessons")

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
        table_font = QFont()
        table_font.setPointSize(18)

        # WordsTable
        self.words_table = QWidget()
        self.words_table_vlayout = QVBoxLayout(self.words_table)
        self.save_btn_words = QPushButton("Save Selected")
        self.select_all_w = QPushButton("Select All")
        self.clear_w = QPushButton("Clear")
        self.words_table_vlayout.addWidget(self.save_btn_words)
        self.words_table_vlayout.addWidget(self.select_all_w)
        self.words_table_vlayout.addWidget(self.clear_w)
        self.table_view_w = QTableView()
        self.table_view_w.setFont(table_font)
        self.table_view_w.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_w.show()

        self.words_table_vlayout.addWidget(self.table_view_w)
        self.stacked_widget.addWidget(self.words_table)

        # SentenceTable
        self.sents_table = QWidget()
        self.save_btn_sents = QPushButton("Save Selected")
        self.select_all_s = QPushButton("Select All")
        self.clear_s = QPushButton("Clear")
        self.sents_table_vlayout = QVBoxLayout(self.sents_table)
        self.sents_table_vlayout.addWidget(self.save_btn_sents)
        self.sents_table_vlayout.addWidget(self.select_all_s)
        self.sents_table_vlayout.addWidget(self.clear_s)
        self.table_view_s = QTableView()
        self.table_view_s.setFont(table_font)
        self.table_view_s.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_s.show()

        self.sents_table_vlayout.addWidget(self.table_view_s)
        self.stacked_widget.addWidget(self.sents_table)

        self.words_page_vlayout.addWidget(self.stacked_widget)

    @Slot(bool)
    def set_lesson_btn(self, disabled):
        self.addwords_btn.setDisabled(disabled)
