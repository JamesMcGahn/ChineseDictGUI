from PySide6.QtCore import Signal
from PySide6.QtWidgets import QRadioButton, QWidget

from .multiword_dialog_ui import MultiWordDialogView


class MultiWordDialog(QWidget):
    md_multi_def_signal = Signal(int)

    def __init__(self, words):
        super().__init__()

        self.ui = MultiWordDialogView()

        for i, word in enumerate(words):
            r = QRadioButton(
                f"{word['chinese']}({word['pinyin']}) - {word['definition'] if len(word['definition']) < 70 else word['definition'][0:70]+'...'}"
            )
            self.ui.select_btn_group.addButton(r, i)
            self.ui.in_dialog_layout.addWidget(r)

        self.ui.select_btn_group.addButton(self.ui.none_btn, len(words))

        self.ui.submit_btn.clicked.connect(self.ok)
        self.ui.cancel_btn.clicked.connect(self.cancel)
        self.ui.dialog_closed.connect(self.handle_close)

    def exec(self):
        self.ui.exec()

    def ok(self):
        self.md_multi_def_signal.emit(self.ui.select_btn_group.checkedId())
        self.ui.accept()

    def handle_close(self):
        self.md_multi_def_signal.emit(9999999)

    def cancel(self):
        self.md_multi_def_signal.emit(9999999)
        self.ui.reject()
