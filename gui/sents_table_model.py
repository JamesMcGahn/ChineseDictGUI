from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal

from dictionary import Sentence


class SentenceTableModel(QAbstractTableModel):
    dataChanged = Signal()

    def __init__(self, sentences=None):
        super().__init__()
        self.sentences = sentences if sentences is not None else []

    def rowCount(self, parent=None):
        return len(self.sentences)

    def columnCount(self, parent=None):
        return 6

    def remove_selected(self, selected):
        indexes = [i.row() for i in selected]
        indexSet = set(indexes)
        filtered_list = [
            sent for index, sent in enumerate(self.sentences) if index not in indexSet
        ]
        self.update_data(filtered_list)

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
                return "Id"
            if section == 1:
                return "Chinese"
            if section == 2:
                return "English"
            if section == 3:
                return "Pinyin"
            if section == 4:
                return "Level"
            if section == 5:
                return "Audio"

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        sentence = self.sentences[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == 0:
                if sentence.id:
                    return sentence.id
                else:
                    return index.row() + 1
            elif index.column() == 1:
                return sentence.chinese
            elif index.column() == 2:
                return sentence.english
            elif index.column() == 3:
                return sentence.pinyin
            elif index.column() == 4:
                return sentence.level
            elif index.column() == 5:
                return sentence.audio
        elif role == Qt.EditRole:
            if index.column() == 1:
                return sentence.chinese
            elif index.column() == 2:
                return sentence.english
            elif index.column() == 3:
                return sentence.pinyin
            elif index.column() == 4:
                return sentence.level
            elif index.column() == 5:
                return sentence.audio

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index: QModelIndex, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            sentence = self.sentences[index.row()]
            if index.column() == 1:
                sentence.chinese = value
            elif index.column() == 2:
                sentence.english = value
            elif index.column() == 3:
                sentence.pinyin = value
            elif index.column() == 4:
                sentence.level = value
            elif index.column() == 5:
                sentence.audio = value
            self.dataChanged.emit()
            return True
        return False

    def get_row_data(self, row_index):
        """Retrieve a dictionary containing all data from a specific row."""
        sentence = self.sentences[row_index]
        print("here is the selectioned", sentence)
        if 0 <= row_index < self.rowCount():
            return Sentence(
                self.data(self.index(row_index, 1), Qt.DisplayRole),
                self.data(self.index(row_index, 2), Qt.DisplayRole),
                self.data(self.index(row_index, 3), Qt.DisplayRole),
                self.data(self.index(row_index, 4), Qt.DisplayRole),
                self.data(self.index(row_index, 5), Qt.DisplayRole),
                sentence.id if sentence.id else None,
            )

        else:
            return None  # Invalid row index
