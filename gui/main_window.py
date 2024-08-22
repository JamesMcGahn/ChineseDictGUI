import resources_rc as resources_rc
from central_widget import CentralWidget
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Custom MainWindow")
        self.setObjectName("MainWindow")
        self.resize(1286, 962)
        self.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setFamilies([".AppleSystemUIFont"])
        self.setFont(font)
        with open("./gui/styles/main_window.css", "r") as ss:
            self.setStyleSheet(ss.read())
        self.centralwidget = CentralWidget()

        self.label = QLabel(self)

        self.setCentralWidget(self.centralwidget)
