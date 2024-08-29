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


class AddLessonsDialog(QDialog):
    add_lesson_submited_signal = Signal(list)

    def __init__(self):
        super().__init__()
        self.lesson_list = []

        self.dialog_vlayout = QVBoxLayout(self)
        self.dialog_vlayout.setSpacing(6)
        self.dialog_vlayout.setContentsMargins(11, 11, 11, 11)
        self.dialog_vlayout.setObjectName("dialog_vlayout")

        self.info_text1 = QLabel("Open a text file or paste the lesson urls below")
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

        self.r_btn_vert_layout.addWidget(self.read_button)
        self.r_btn_vert_layout.addItem(self.verticalSpacer)

        self.text_edit_horz_layout.addWidget(self.textEdit)
        self.text_edit_horz_layout.addLayout(self.r_btn_vert_layout)

        self.dialog_vlayout.addWidget(self.info_text1)
        self.dialog_vlayout.addWidget(self.info_text2)
        self.dialog_vlayout.addLayout(self.text_edit_horz_layout)

        self.dialog_vlayout.addLayout(self.horizontalLayout_3)

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

    def cancel_btn_clicked(self):
        self.reject()

    def submit_btn_clicked(self):
        self.add_lesson_submited_signal.emit(self.textEdit.toPlainText().split("\n"))
        self.textEdit.clear()
        self.lesson_list = []

        self.accept()
