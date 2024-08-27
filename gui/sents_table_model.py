from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal


class SentenceTableModel(QAbstractTableModel):
    dataChanged = Signal()

    def __init__(self, sentences=None):
        super().__init__()
        self.sentences = sentences if sentences is not None else []

    def rowCount(self, parent=None):
        return len(self.sentences)

    def columnCount(self, parent=None):
        return 5

    def update_data(self, sentences):
        self.beginResetModel()
        self.sentences = sentences
        self.endResetModel()

    def add_sentence(self, sentence):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.sentences.append(sentence)
        self.endInsertRows()

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Chinese"
            if section == 1:
                return "English"
            if section == 2:
                return "Pinyin"
            if section == 3:
                return "Level"
            if section == 4:
                return "Audio"

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        sentence = self.sentences[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return sentence.chinese
            elif index.column() == 1:
                return sentence.english
            elif index.column() == 2:
                return sentence.pinyin
            elif index.column() == 3:
                return sentence.level
            elif index.column() == 4:
                return sentence.audio
        elif role == Qt.EditRole:
            if index.column() == 0:
                return sentence.chinese
            elif index.column() == 1:
                return sentence.english
            elif index.column() == 2:
                return sentence.pinyin
            elif index.column() == 3:
                return sentence.level
            elif index.column() == 4:
                return sentence.audio

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index: QModelIndex, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            sentence = self.sentences[index.row()]
            if index.column() == 0:
                sentence.chinese = value
            elif index.column() == 1:
                sentence.english = value
            elif index.column() == 2:
                sentence.pinyin = value
            elif index.column() == 3:
                sentence.level = value
            elif index.column() == 4:
                sentence.audio = value
            self.dataChanged.emit()
            return True
        return False
