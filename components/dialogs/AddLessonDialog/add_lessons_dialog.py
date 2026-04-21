from PySide6.QtCore import QFile, QIODevice, QTextStream, Signal
from PySide6.QtWidgets import QFileDialog, QWidget

from services.lessons import LessonRequestBuilder

from .add_lessons_dialog_ui import AddLessonsDialogView


class AddLessonsDialog(QWidget):
    add_lesson_submited_signal = Signal(list)
    add_lesson_closed = Signal()
    reset_form_ui = Signal()
    set_lesson_text_edit = Signal(str)

    def __init__(self):
        super().__init__()
        self.lesson_request_builder = LessonRequestBuilder()
        self.lesson_list = []

        self.check_for_dup_words = False
        self.check_for_dup_sents = False
        self.transcribe_lesson = True

        self.ui = AddLessonsDialogView()
        self.reset_form_ui.connect(self.ui.reset_form)
        self.set_lesson_text_edit.connect(self.ui.set_lesson_text_edit)
        self.ui.read_button.clicked.connect(self.read_button_clicked)
        self.ui.submit_btn.clicked.connect(self.submit_btn_clicked)
        self.ui.cancel_btn.clicked.connect(self.cancel_btn_clicked)
        self.ui.check_for_sent_dups_cb.toggled.connect(self.check_for_dup_sents_toggle)
        self.ui.check_for_word_dups_cb.toggled.connect(self.check_for_dup_words_toggle)
        self.ui.transcribe_lesson_cb.toggled.connect(self.transcribe_lesson_toggle)

    def exec(self):
        self.ui.exec()

    def read_button_clicked(self):
        file_content = ""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "./", "Text(*.txt)"
        )
        if file_name == "":
            return

        file = QFile(file_name)
        if not file.open(QIODevice.ReadOnly | QIODevice.Text):
            return

        in_stream = QTextStream(file)

        while not in_stream.atEnd():
            line = in_stream.readLine()
            file_content += line
            file_content += "\n"
        file.close()
        self.set_lesson_text_edit.emit(file_content)

    def cancel_btn_clicked(self):
        self.ui.reject()

    def check_for_dup_words_toggle(self, checked):
        if checked:
            self.check_for_dup_words = True
        else:
            self.check_for_dup_words = False

    def check_for_dup_sents_toggle(self, checked):
        if checked:
            self.check_for_dup_sents = True
        else:
            self.check_for_dup_sents = False

    def transcribe_lesson_toggle(self, checked):
        if checked:
            self.transcribe_lesson = True
        else:
            self.transcribe_lesson = False

    def reset_form(self):
        self.check_for_dup_sents_toggle(False)
        self.check_for_dup_words_toggle(False)
        self.transcribe_lesson_toggle(False)
        self.reset_form_ui.emit()

    def submit_btn_clicked(self):

        text = self.ui.get_text_from_lesson_text_edit()
        requests = self.lesson_request_builder.build_request_from_text(
            text,
            self.check_for_dup_sents,
            self.check_for_dup_words,
            self.transcribe_lesson,
        )
        self.add_lesson_submited_signal.emit(requests)
        self.reset_form()
        self.ui.accept()
