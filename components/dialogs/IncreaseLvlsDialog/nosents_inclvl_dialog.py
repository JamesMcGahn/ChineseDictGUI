from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from .nosents_inclvl_dialog_ui import IncreaseLvlsDialogView


class IncreaseLvlsDialog(QWidget):
    sent_lvls_change_sig = Signal(bool, list)

    def __init__(self, level_selection):
        super().__init__()

        self.ui = IncreaseLvlsDialogView()

        self.level_selection = level_selection
        self.selection_changed = False

        for i, _ in enumerate(self.level_selection):
            item = self.ui.sent_filt_ql.item(i)
            if item.text() in self.level_selection:
                item.setSelected(True)

        self.ui.info_text1.setText(
            f"There are no sentences for the level{'s' if len(self.level_selection) > 1 else ''} selected. "
        )

        self.ui.sent_filt_ql.itemSelectionChanged.connect(self.sent_filt_ql_changed)
        self.ui.submit_btn.clicked.connect(self.submit_btn_clicked)
        self.ui.cancel_btn.clicked.connect(self.cancel_btn_clicked)

    def exec(self):
        self.ui.exec()

    def sent_filt_ql_changed(self):
        self.selection_changed = True
        self.level_selection = [x.text() for x in self.ui.sent_filt_ql.selectedItems()]

    def cancel_btn_clicked(self):
        self.sent_lvls_change_sig.emit(False, [])
        self.ui.reject()

    def submit_btn_clicked(self):
        if self.selection_changed:
            self.sent_lvls_change_sig.emit(True, self.level_selection)
        else:
            self.sent_lvls_change_sig.emit(False, [])

        self.ui.sent_filt_ql.clearSelection()
        self.level_selection = False

        self.ui.accept()
