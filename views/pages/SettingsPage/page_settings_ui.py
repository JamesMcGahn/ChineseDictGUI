from PySide6.QtCore import QRect, QSize, Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from components.utils import ColoredSpacer

from .field_registry import FieldRegistry
from .tabs.app_settings import TabAppSettings
from .tabs.log_settings import TabLogSettings


class PageSettingsUI(QWidget):
    folder_submit = Signal(str, str)
    secure_setting_change = Signal(str, str)

    def __init__(self, ui_helper):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.app_settings_tab = TabAppSettings()
        self.log_settings_tab = TabLogSettings()

        self.tabs.addTab(self.app_settings_tab, QIcon(), "App Settings")
        self.tabs.addTab(self.log_settings_tab, QIcon(), "Log Settings")

        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setTabsClosable(False)
        self.layout.addWidget(self.tabs)
