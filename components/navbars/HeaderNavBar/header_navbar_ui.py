import os

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


class HeaderNavBarView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setObjectName("header_widget_ui")

        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )

        self.navbar_vlayout = QVBoxLayout(self)
        self.navbar_vlayout.setObjectName("navbar_vlayout")

        self.inner_cont_hlayout = QHBoxLayout()
        self.inner_cont_hlayout.setObjectName("inner_cont_hlayout")

        self.app_logo_vlayout = QVBoxLayout()
        self.app_logo_vlayout.setObjectName("app_logo_vlayout")

        self.app_logo = QLabel(self)
        self.app_logo.setObjectName("app_logo")
        self.app_logo.setStyleSheet("text-align: right;")
        self.app_logo.setPixmap(QPixmap(":/ /images/logo.png"))

        self.app_logo_vlayout.addWidget(self.app_logo)

        self.horizontalSpacer_3 = QSpacerItem(
            558, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.inner_cont_hlayout.addLayout(self.app_logo_vlayout)
        self.inner_cont_hlayout.addItem(self.horizontalSpacer_3)

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

        self.inner_cont_hlayout.addWidget(self.lineEdit)

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

        self.inner_cont_hlayout.addWidget(self.hamburger_icon_btn)

        self.navbar_vlayout.addLayout(self.inner_cont_hlayout)
