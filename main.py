import os
import sys

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from views import MainWindow


def main():
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    os.environ["OMP_NUM_THREADS"] = "1"
    QCoreApplication.setOrganizationName("ChineseDictGUI")
    QCoreApplication.setApplicationName("ChineseDictGUI")
    QCoreApplication.setApplicationVersion("0.1.0")
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
