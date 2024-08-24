from add_words_dialog import AddWordsDialog
from PySide6.QtCore import QRect, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class PageWords(QWidget):
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

        self.dialog = AddWordsDialog()

        self.addwords_btn.clicked.connect(self.addwords_btn_clicked)

        self.dialog.add_words_submited_signal.connect(self.get_dialog_submitted)

    def addwords_btn_clicked(self):
        self.dialog.exec()

    @Slot(dict)
    def get_dialog_submitted(self, form_data):
        print("slot", form_data)
