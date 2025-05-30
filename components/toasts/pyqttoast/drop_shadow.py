from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from .css.drop_shadow_css import DROP_SHADOW_CSS


class DropShadow(QWidget):
    def __init__(self, parent: QWidget = None):
        """Create a new DropShadow instance

        :param parent: the parent widget
        """

        super(DropShadow, self).__init__(parent)

        # Drawn manually since only one graphics effect can be applied
        self.layer_1 = QWidget(self)
        self.layer_1.setObjectName("drop-shadow-layer-1")

        self.layer_2 = QWidget(self)
        self.layer_2.setObjectName("drop-shadow-layer-2")

        self.layer_3 = QWidget(self)
        self.layer_3.setObjectName("drop-shadow-layer-3")

        self.layer_4 = QWidget(self)
        self.layer_4.setObjectName("drop-shadow-layer-4")

        self.layer_5 = QWidget(self)
        self.layer_5.setObjectName("drop-shadow-layer-5")

        # Apply stylesheet
        self.setStyleSheet(DROP_SHADOW_CSS)

    def resize(self, size: QSize):
        """Resize the drop shadow widget

        :param size: new size
        """

        super().resize(size)
        width = size.width()
        height = size.height()

        self.layer_1.resize(width, height)
        self.layer_1.move(0, 0)
        self.layer_2.resize(width - 2, height - 2)
        self.layer_2.move(1, 1)
        self.layer_3.resize(width - 4, height - 4)
        self.layer_3.move(2, 2)
        self.layer_4.resize(width - 6, height - 6)
        self.layer_4.move(3, 3)
        self.layer_5.resize(width - 8, height - 8)
        self.layer_5.move(4, 4)
