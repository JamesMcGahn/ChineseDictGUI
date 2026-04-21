from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
)


class AddLessonsDialogView(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.resize(900, 500)
        self.dialog_vlayout = QVBoxLayout()
        self.dialog_vlayout.setSpacing(6)
        self.dialog_vlayout.setContentsMargins(11, 11, 11, 11)
        self.dialog_vlayout.setObjectName("add_lesson_dialog_vlayout")

        self.info_text1 = QLabel("Open a text file or paste the lesson urls below")
        self.info_text2 = QLabel("Words should be new line separated")

        self.text_edit_horz_layout = QHBoxLayout()
        self.text_edit_horz_layout.setSpacing(6)
        self.text_edit_horz_layout.setObjectName("text_edit_horz_layout")
        self.lesson_input_text_edit = QTextEdit()
        self.lesson_input_text_edit.setObjectName("lesson_input_text_edit")

        self.r_btn_vert_layout = QVBoxLayout()
        self.r_btn_vert_layout.setSpacing(6)
        self.r_btn_vert_layout.setObjectName("r_btn_vert_layout")
        self.write_button = QPushButton()

        self.read_button = QPushButton("Open .txt")
        self.read_button.setObjectName("read_button")

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
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

        self.r_btn_vert_layout.addWidget(self.read_button)
        self.r_btn_vert_layout.addItem(self.verticalSpacer)

        self.text_edit_horz_layout.addWidget(self.lesson_input_text_edit)
        self.text_edit_horz_layout.addLayout(self.r_btn_vert_layout)

        self.dialog_vlayout.addWidget(self.info_text1)
        self.dialog_vlayout.addWidget(self.info_text2)
        self.dialog_vlayout.addLayout(self.text_edit_horz_layout)

        self.check_for_dups_hlayout = QHBoxLayout()
        self.transcribe_lesson_hlayout = QHBoxLayout()
        self.check_for_sent_dups_lb = QLabel("Check For Duplicate Sentences?")
        self.check_for_sent_dups_cb = QCheckBox()
        self.check_for_word_dups_lb = QLabel("Check For Duplicate Words?")
        self.check_for_word_dups_cb = QCheckBox()
        self.transcribe_lesson_lb = QLabel("Do you want the lesson transcribed?")
        self.transcribe_lesson_cb = QCheckBox()
        self.transcribe_lesson_cb.setChecked(True)
        self.check_for_dups_hlayout.addWidget(self.check_for_sent_dups_lb)
        self.check_for_dups_hlayout.addWidget(self.check_for_sent_dups_cb)
        self.check_for_dups_hlayout.addWidget(self.check_for_word_dups_lb)
        self.check_for_dups_hlayout.addWidget(self.check_for_word_dups_cb)
        self.transcribe_lesson_hlayout.addWidget(self.transcribe_lesson_lb)
        self.transcribe_lesson_hlayout.addWidget(self.transcribe_lesson_cb)
        self.dialog_vlayout.addLayout(self.check_for_dups_hlayout)
        self.dialog_vlayout.addLayout(self.transcribe_lesson_hlayout)
        self.dialog_vlayout.addLayout(self.submit_cnl_h_layout)

        self.setLayout(self.dialog_vlayout)

    def reset_form(self):
        self.lesson_input_text_edit.clear()
        self.transcribe_lesson_cb.setChecked(False)
        self.check_for_sent_dups_cb.setChecked(False)
        self.check_for_word_dups_cb.setChecked(False)

    def get_text_from_lesson_text_edit(self):
        return self.lesson_input_text_edit.toPlainText().split("\n")

    def set_lesson_text_edit(self, text):
        self.lesson_input_text_edit.clear()
        self.lesson_input_text_edit.setText(text)
