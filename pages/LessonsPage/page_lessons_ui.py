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

        self.table_view_w = QTableView()
        self.table_view_w.show()

        self.words_table_vlayout.addWidget(self.table_view_w)
        self.stacked_widget.addWidget(self.words_table)

        # SentenceTable
        self.sents_table = QWidget()
        self.sents_table_vlayout = QVBoxLayout(self.sents_table)

        self.table_view_s = QTableView()
        self.table_view_s.show()

        self.sents_table_vlayout.addWidget(self.table_view_s)
        self.stacked_widget.addWidget(self.sents_table)

        self.words_page_vlayout.addWidget(self.stacked_widget)