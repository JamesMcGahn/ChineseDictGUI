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


class IncreaseLvlsDialogView(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.dialog_vlayout = QVBoxLayout()
        self.dialog_vlayout.setSpacing(6)
        self.dialog_vlayout.setContentsMargins(11, 11, 11, 11)
        self.dialog_vlayout.setObjectName("dialog_vlayout")

        self.info_text1 = QLabel()
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
        self.setLayout(self.dialog_vlayout)
