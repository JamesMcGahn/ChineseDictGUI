from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
)


class AddWordsDialogView(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.dialog_vlayout = QVBoxLayout()
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

        self.submit_cnl_h_layout = QHBoxLayout()
        self.submit_cnl_h_layout.setObjectName("submit_cnl_h_layout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.submit_cnl_h_layout.addItem(self.horizontalSpacer)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setObjectName("submit_button")

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_button")

        self.submit_cnl_h_layout.addWidget(self.cancel_btn)
        self.submit_cnl_h_layout.addWidget(self.submit_btn)

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
        self.dialog_vlayout.addLayout(self.submit_cnl_h_layout)

        self.setLayout(self.dialog_vlayout)
