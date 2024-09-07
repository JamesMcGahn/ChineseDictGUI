from PySide6.QtCore import QFile, QIODevice, QTextStream, Signal
from PySide6.QtWidgets import QFileDialog, QWidget

from .add_words_dialog_ui import AddWordsDialogView


class AddWordsDialog(QWidget):
    add_words_submited_signal = Signal(dict)

    def __init__(self, word_list=None):
        super().__init__()
        self.ui = AddWordsDialogView()

        self.word_list = word_list
        self.definition_source = "Cpod"
        self.save_sentences = False
        self.level_selection = False

        if word_list is not None:
            self.ui.textEdit.setText(self.word_list)

        self.ui.def_src_combo.currentTextChanged.connect(self.def_src_combo_changed)
        self.ui.read_button.clicked.connect(self.read_button_clicked)

        self.ui.ex_sents_cb.toggled.connect(self.ex_sents_cb_toggle)
        self.ui.filt_sents_cb.toggled.connect(self.filt_sents_cb_toggle)

        self.ui.sent_filt_ql.itemSelectionChanged.connect(self.sent_filt_ql_changed)

        self.ui.submit_btn.clicked.connect(self.submit_btn_clicked)
        self.ui.cancel_btn.clicked.connect(self.cancel_btn_clicked)

    def exec(self):
        self.ui.exec()

    def read_button_clicked(self):
        file_content = ""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "./", "Text(*.txt)"
        )
        if file_name == "":
            return
        print("filename", file_name)
        file = QFile(file_name)
        if not file.open(QIODevice.ReadOnly | QIODevice.Text):
            return
        in_stream = QTextStream(file)
        while not in_stream.atEnd():
            line = in_stream.readLine()
            file_content += line
            file_content += "\n"
        file.close()
        self.ui.textEdit.clear()

        self.ui.textEdit.setText(file_content)

    def ex_sents_cb_toggle(self, checked):
        if checked:
            self.ui.filt_sents_cb.setHidden(False)
            self.ui.filt_sents_lb.setHidden(False)
            self.save_sentences = True
        else:
            self.ui.filt_sents_cb.setHidden(True)
            self.ui.filt_sents_lb.setHidden(True)
            self.save_sentences = False

    def filt_sents_cb_toggle(self, checked):
        if checked:
            self.ui.sent_filt_lb.setHidden(False)
            self.ui.sent_filt_ql.setHidden(False)
        else:
            self.ui.sent_filt_lb.setHidden(True)
            self.ui.sent_filt_ql.setHidden(True)
            self.level_selection = False

    def sent_filt_ql_changed(self):
        self.level_selection = [x.text() for x in self.ui.sent_filt_ql.selectedItems()]

    def def_src_combo_changed(self, selection):
        self.definition_source = selection

    def cancel_btn_clicked(self):
        self.ui.reject()

    def submit_btn_clicked(self):
        self.form = {
            "word_list": self.ui.textEdit.toPlainText().split("\n"),
            "definition_source": self.definition_source,
            "save_sentences": self.save_sentences,
            "level_selection": self.level_selection,
        }
        self.add_words_submited_signal.emit(self.form)
        self.ui.textEdit.clear()
        self.word_list = []
        self.definition_source = "Cpod"
        self.ui.def_src_combo.setCurrentIndex(0)
        self.ui.ex_sents_cb.setChecked(False)
        self.save_sentences = False
        self.ui.filt_sents_cb.setChecked(False)
        self.ui.sent_filt_ql.clearSelection()
        self.level_selection = False

        self.ui.accept()
