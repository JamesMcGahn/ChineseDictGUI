from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class HeaderNavBar(QWidget):
    hamburger_signal = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setObjectName("header_widget")
        self.setMaximumSize(QSize(16777215, 175))
        self.setAttribute(Qt.WA_StyledBackground, True)
        with open("./styles/header_navbar.css", "r") as ss:
            self.setStyleSheet(ss.read())

        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )

        self.verticalLayout_7 = QVBoxLayout(self)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QLabel(self)
        self.label.setObjectName("label")
        self.label.setStyleSheet("text-align: right;")
        self.label.setPixmap(QPixmap(":/ /images/logo.png"))

        self.verticalLayout_3.addWidget(self.label)

        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.horizontalSpacer_3 = QSpacerItem(
            558, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setObjectName("lineEdit")
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QSize(250, 31))
        self.lineEdit.setMaximumSize(QSize(250, 31))
        self.lineEdit.setStyleSheet(
            "QLineEdit {\n"
            "	padding-left: 20px;\n"
            "	border: 1px solid gray;\n"
            "	border-radius: 10px;\n"
            "}"
        )

        self.horizontalLayout_2.addWidget(self.lineEdit)

        self.hamburger_icon_btn = QPushButton(self)
        self.hamburger_icon_btn.setObjectName("hamburger-icon-btn")
        self.hamburger_icon_btn.setStyleSheet(
            "QPushButton {\n" "border: none;\n" "padding-right:.5em\n" "}"
        )
        icon6 = QIcon()
        icon6.addFile(
            ":/ /images/hamburger_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        icon6.addFile(
            ":/ /images/hamburger_on.png", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        self.hamburger_icon_btn.setIcon(icon6)
        self.hamburger_icon_btn.setIconSize(QSize(29, 35))
        self.hamburger_icon_btn.setCheckable(True)

        self.horizontalLayout_2.addWidget(self.hamburger_icon_btn)

        self.verticalLayout_7.addLayout(self.horizontalLayout_2)

        self.hamburger_icon_btn.toggled.connect(self.hamburger_icon_btn_toggled)

    def hamburger_icon_btn_toggled(self):
        self.hamburger_signal.emit(self.hamburger_icon_btn.isChecked())