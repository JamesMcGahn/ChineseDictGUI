from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class IncreaseLvlsDialog(QDialog):
    sent_lvls_change_sig = Signal(bool, list)

    def __init__(self, level_selection):
        super().__init__()

        self.level_selection = level_selection

        self.dialog_vlayout = QVBoxLayout(self)
        self.dialog_vlayout.setSpacing(6)
        self.dialog_vlayout.setContentsMargins(11, 11, 11, 11)
        self.dialog_vlayout.setObjectName("dialog_vlayout")
        self.selection_changed = False

        self.info_text1 = QLabel(
            f"There are no sentences for the level{'s' if len(self.level_selection) > 1 else ''} selected. "
        )
        self.info_text2 = QLabel("Would you like to add more levels?")

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

        for i, _ in enumerate(self.level_selection):
            item = self.sent_filt_ql.item(i)
            if item.text() in self.level_selection:
                item.setSelected(True)

        self.sub_can_btn_hlayout = QHBoxLayout()
        self.sub_can_btn_hlayout.setObjectName("sub_can_btn_hlayout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.sub_can_btn_hlayout.addItem(self.horizontalSpacer)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setObjectName("submit_button")

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_button")

        self.sub_can_btn_hlayout.addWidget(self.cancel_btn)
        self.sub_can_btn_hlayout.addWidget(self.submit_btn)

        self.dialog_vlayout.addWidget(self.info_text1)
        self.dialog_vlayout.addWidget(self.info_text2)

        self.dialog_vlayout.addWidget(self.sent_filt_lb)
        self.dialog_vlayout.addWidget(self.sent_filt_ql)
        self.dialog_vlayout.addLayout(self.sub_can_btn_hlayout)

        self.sent_filt_ql.itemSelectionChanged.connect(self.sent_filt_ql_changed)

        self.submit_btn.clicked.connect(self.submit_btn_clicked)
        self.cancel_btn.clicked.connect(self.cancel_btn_clicked)

    def sent_filt_ql_changed(self):
        self.selection_changed = True
        self.level_selection = [x.text() for x in self.sent_filt_ql.selectedItems()]

    def cancel_btn_clicked(self):
        self.sent_lvls_change_sig.emit(False, [])
        self.reject()

    def submit_btn_clicked(self):
        if self.selection_changed:
            self.sent_lvls_change_sig.emit(True, self.level_selection)
        else:
            self.sent_lvls_change_sig.emit(False, [])

        self.sent_filt_ql.clearSelection()
        self.level_selection = False

        self.accept()
