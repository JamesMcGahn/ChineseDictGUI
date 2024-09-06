from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class MultiWordDialog(QDialog):
    md_multi_def_signal = Signal(int)

    def __init__(self, words):
        super().__init__()

        self.setWindowTitle("Pop up window")

        dialog_layout = QVBoxLayout(self)
        self.label = QLabel("Choose a Defintion")
        dialog_layout.addWidget(self.label)
        self.select_btn_group = QButtonGroup()

        for i, word in enumerate(words):
            r = QRadioButton(
                f"{word['chinese']}({word['pinyin']}) - {word['definition'] if len(word['definition']) < 70 else word['definition'][0:70]+'...'}"
            )
            self.select_btn_group.addButton(r, i)
            dialog_layout.addWidget(r)
        none_btn = QRadioButton("None of these")
        self.select_btn_group.addButton(none_btn, len(words))
        dialog_layout.addWidget(none_btn)
        self.dialog_md_hlayout = QHBoxLayout()
        self.dialog_md_hlayout.setObjectName("dialog_md_hlayout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        self.dialog_md_hlayout.addItem(self.horizontalSpacer)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setObjectName("submit_button")

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_button")

        self.dialog_md_hlayout.addWidget(self.cancel_btn)
        self.dialog_md_hlayout.addWidget(self.submit_btn)

        dialog_layout.addLayout(self.dialog_md_hlayout)

        self.submit_btn.clicked.connect(self.ok)
        self.cancel_btn.clicked.connect(self.cancel)

    def ok(self):
        self.md_multi_def_signal.emit(self.select_btn_group.checkedId())
        self.accept()

    def cancel(self):
        self.reject()
