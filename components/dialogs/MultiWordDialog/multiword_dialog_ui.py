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


class MultiWordDialogView(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Found Multiple Definitions")

        self.dialog_layout = QVBoxLayout()
        self.label = QLabel("Choose a Defintion")
        self.dialog_layout.addWidget(self.label)
        self.select_btn_group = QButtonGroup()

        self.in_dialog_layout = QVBoxLayout()

        self.none_btn = QRadioButton("None of these")
        self.in_dialog_layout.addWidget(self.none_btn)

        self.dialog_layout.addLayout(self.in_dialog_layout)
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

        self.dialog_layout.addLayout(self.dialog_md_hlayout)
        self.setLayout(self.dialog_layout)
