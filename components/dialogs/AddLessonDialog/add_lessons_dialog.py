from PySide6.QtCore import QFile, QIODevice, QTextStream, Signal
from PySide6.QtWidgets import QFileDialog, QWidget

from models.dictionary import Lesson

from .add_lessons_dialog_ui import AddLessonsDialogView


class AddLessonsDialog(QWidget):
    add_lesson_submited_signal = Signal(list, bool, bool)
    add_lesson_closed = Signal()

    def __init__(self):
        super().__init__()
        self.lesson_list = []

        self.check_for_dups = False
        self.transcribe_lesson = True

        self.ui = AddLessonsDialogView()
        self.ui.read_button.clicked.connect(self.read_button_clicked)
        self.ui.submit_btn.clicked.connect(self.submit_btn_clicked)
        self.ui.cancel_btn.clicked.connect(self.cancel_btn_clicked)
        self.ui.check_for_dups_cb.toggled.connect(self.check_for_dups_toggle)
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

        self.ui.textEdit.clear()
        self.ui.textEdit.setText(file_content)

    def cancel_btn_clicked(self):
        self.ui.reject()

    def check_for_dups_toggle(self, checked):
        if checked:
            self.check_for_dups = True
        else:
            self.check_for_dups = False

    def transcribe_lesson_toggle(self, checked):
        if checked:
            self.transcribe_lesson = True
        else:
            self.transcribe_lesson = False

    def submit_btn_clicked(self):

        urls = self.ui.textEdit.toPlainText().split("\n")
        lesson_urls = [x.strip() for x in urls if x]
        lessons = []
        for url in lesson_urls:
            if "chinesepod" in url:
                less = Lesson(
                    provider="cpod",
                    url=url,
                    slug="",
                    check_dup_sents=self.check_for_dups,
                    transcribe_lesson=self.transcribe_lesson,
                )
                lessons.append(less)

        self.add_lesson_submited_signal.emit(
            lessons,
            self.check_for_dups,
            self.transcribe_lesson,
        )
        self.ui.textEdit.clear()
        self.check_for_dups = False
        self.ui.check_for_dups_cb.setChecked(False)
        self.lesson_list = []

        self.ui.accept()
