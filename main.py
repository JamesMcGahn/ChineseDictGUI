import sys

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from views import MainWindow


def main():

    QCoreApplication.setOrganizationName("ChineseDictGUI")
    QCoreApplication.setApplicationName("ChineseDictGUI")
    QCoreApplication.setApplicationVersion("0.1.0")

    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()

    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )


if __name__ == "__main__":
    raise SystemExit(main())
