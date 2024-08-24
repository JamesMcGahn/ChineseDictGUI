from PySide6.QtCore import QFile, QIODevice, QTextStream, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
)


class AddWordsDialog(QDialog):
    add_words_submited_signal = Signal(dict)

    def __init__(self):
        super().__init__()
        self.word_list = []
        self.definition_source = "Cpod"
        self.save_sentences = False
        self.level_selection = False

        self.dialog_vlayout = QVBoxLayout(self)
        self.dialog_vlayout.setSpacing(6)
        self.dialog_vlayout.setContentsMargins(11, 11, 11, 11)
        self.dialog_vlayout.setObjectName("dialog_vlayout")

        self.info_text1 = QLabel("Open a text file or paste the words below")
        self.info_text2 = QLabel("Words should be new line separated")

        self.text_edit_horz_layout = QHBoxLayout()
        self.text_edit_horz_layout.setSpacing(6)
        self.text_edit_horz_layout.setObjectName("text_edit_horz_layout")
        self.textEdit = QTextEdit()
        self.textEdit.setObjectName("textEdit")

        self.r_btn_vert_layout = QVBoxLayout()
        self.r_btn_vert_layout.setSpacing(6)
        self.r_btn_vert_layout.setObjectName("r_btn_vert_layout")
        self.write_button = QPushButton()
        self.write_button.setObjectName("write_button")

        self.read_button = QPushButton("Open .txt")
        self.read_button.setObjectName("read_button")

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.def_src_hlayout = QHBoxLayout()
        self.def_src_label = QLabel("Where should we grab definitions from?")
        self.def_src_combo = QComboBox()
        self.def_src_combo.addItems(["Cpod", "MDGB"])

        self.ex_sents_hlayout = QHBoxLayout()
        self.ex_sents_lb = QLabel("Do you want Example Sentences?")
        self.ex_sents_cb = QCheckBox()
        self.ex_sents_hlayout.addWidget(self.ex_sents_lb)
        self.ex_sents_hlayout.addWidget(self.ex_sents_cb)

        self.filt_sents_hlayout = QHBoxLayout()
        self.filt_sents_lb = QLabel("Do you want to filter sentences by level?: ")
        self.filt_sents_cb = QCheckBox()
        self.filt_sents_hlayout.addWidget(self.filt_sents_lb)
        self.filt_sents_hlayout.addWidget(self.filt_sents_cb)

        self.sent_filt_lb = QLabel("Please select levels: ")
        self.sent_filt_ql = QListWidget()
        self.sent_filt_ql.setSelectionMode(QAbstractItemView.MultiSelection)

        self.sent_filt_ql.addItems(
            [
                "Newbie",
                "Elementary",
                "Pre-Intermediate",
                "Intermediate",
                "Advanced",
            ]
        )

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setObjectName("submit_button")

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_button")

        self.horizontalLayout_3.addWidget(self.cancel_btn)
        self.horizontalLayout_3.addWidget(self.submit_btn)

        self.filt_sents_lb.setHidden(True)
        self.filt_sents_cb.setHidden(True)
        self.sent_filt_lb.setHidden(True)
        self.sent_filt_ql.setHidden(True)

        self.r_btn_vert_layout.addWidget(self.read_button)
        self.r_btn_vert_layout.addItem(self.verticalSpacer)

        self.text_edit_horz_layout.addWidget(self.textEdit)
        self.text_edit_horz_layout.addLayout(self.r_btn_vert_layout)

        self.dialog_vlayout.addWidget(self.info_text1)
        self.dialog_vlayout.addWidget(self.info_text2)
        self.dialog_vlayout.addLayout(self.text_edit_horz_layout)
        self.dialog_vlayout.addWidget(self.def_src_label)
        self.dialog_vlayout.addWidget(self.def_src_combo)
        self.dialog_vlayout.addLayout(self.def_src_hlayout)
        self.dialog_vlayout.addLayout(self.ex_sents_hlayout)
        self.dialog_vlayout.addLayout(self.filt_sents_hlayout)
        self.dialog_vlayout.addWidget(self.sent_filt_lb)
        self.dialog_vlayout.addWidget(self.sent_filt_ql)
        self.dialog_vlayout.addLayout(self.horizontalLayout_3)

        self.def_src_combo.currentTextChanged.connect(self.def_src_combo_changed)
        self.read_button.clicked.connect(self.read_button_clicked)

        self.ex_sents_cb.toggled.connect(self.ex_sents_cb_toggle)
        self.filt_sents_cb.toggled.connect(self.filt_sents_cb_toggle)

        self.sent_filt_ql.itemSelectionChanged.connect(self.sent_filt_ql_changed)

        self.submit_btn.clicked.connect(self.submit_btn_clicked)
        self.cancel_btn.clicked.connect(self.cancel_btn_clicked)

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
        self.textEdit.clear()

        self.textEdit.setText(file_content)

    def ex_sents_cb_toggle(self, checked):
        if checked:
            self.filt_sents_cb.setHidden(False)
            self.filt_sents_lb.setHidden(False)
            self.save_sentences = True
        else:
            self.filt_sents_cb.setHidden(True)
            self.filt_sents_lb.setHidden(True)
            self.save_sentences = False

    def filt_sents_cb_toggle(self, checked):
        if checked:
            self.sent_filt_lb.setHidden(False)
            self.sent_filt_ql.setHidden(False)
        else:
            self.sent_filt_lb.setHidden(True)
            self.sent_filt_ql.setHidden(True)
            self.level_selection = False

    def sent_filt_ql_changed(self):
        self.level_selection = [x.text() for x in self.sent_filt_ql.selectedItems()]

    def def_src_combo_changed(self, selection):
        self.definition_source = selection

    def cancel_btn_clicked(self):
        self.reject()

    def submit_btn_clicked(self):
        self.word_list = [
            x.strip() for x in self.textEdit.toPlainText().split("\n") if x != ""
        ]
        form = {
            "word_list": self.word_list,
            "definition_source": self.definition_source,
            "save_sentences": self.save_sentences,
            "level_selection": self.level_selection,
        }

        self.add_words_submited_signal.emit(form)

        self.textEdit.clear()
        self.word_list = []
        self.definition_source = "Cpod"
        self.def_src_combo.setCurrentIndex(0)
        self.ex_sents_cb.setChecked(False)
        self.save_sentences = False
        self.filt_sents_cb.setChecked(False)
        self.sent_filt_ql.clearSelection()
        self.level_selection = False

        self.accept()
