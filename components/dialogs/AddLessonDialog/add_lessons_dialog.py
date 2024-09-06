from PySide6.QtCore import QFile, QIODevice, QTextStream, Signal
from PySide6.QtWidgets import QFileDialog, QWidget

from .add_lessons_dialog_ui import AddLessonsDialogView


class AddLessonsDialog(QWidget):
    add_lesson_submited_signal = Signal(list)

    def __init__(self):
        super().__init__()
        self.lesson_list = []

        self.ui = AddLessonsDialogView()
        self.ui.read_button.clicked.connect(self.read_button_clicked)
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

    def submit_btn_clicked(self):
        self.add_lesson_submited_signal.emit(self.ui.textEdit.toPlainText().split("\n"))
        self.ui.textEdit.clear()
        self.lesson_list = []

        self.ui.accept()
