from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal

from dictionary import Word


class WordTableModel(QAbstractTableModel):
    dataChanged = Signal()

    def __init__(self, words=None):
        super().__init__()
        self.words = words if words is not None else []

    def rowCount(self, parent=None):
        return len(self.words)

    def columnCount(self, parent=None):
        return 6

    def remove_selected(self, selected):
        indexes = [i.row() for i in selected]
        indexSet = set(indexes)
        filtered_list = [
            word for index, word in enumerate(self.words) if index not in indexSet
        ]
        self.update_data(filtered_list)

    def update_data(self, words):
        self.beginResetModel()
        self.words = words
        self.endResetModel()

    def add_word(self, word):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.words.append(word)
        self.endInsertRows()

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Id"
            if section == 1:
                return "Chinese"
            if section == 2:
                return "Pinyin"
            if section == 3:
                return "Definition"
            if section == 4:
                return "Level"
            if section == 5:
                return "Audio"

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        word = self.words[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == 0:
                if word.id:
                    return word.id
                else:
                    return index.row() + 1
            elif index.column() == 1:
                return word.chinese
            elif index.column() == 2:
                return word.pinyin
            elif index.column() == 3:
                return word.definition
            elif index.column() == 4:
                return word.level
            elif index.column() == 5:
                return word.audio
        elif role == Qt.EditRole:
            if index.column() == 1:
                return word.chinese
            elif index.column() == 2:
                return word.pinyin
            elif index.column() == 3:
                return word.definition
            elif index.column() == 4:
                return word.level
            elif index.column() == 5:
                return word.audio

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index: QModelIndex, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            word = self.words[index.row()]
            if index.column() == 1:
                word.chinese = value
            elif index.column() == 2:
                word.pinyin = value
            elif index.column() == 3:
                word.definition = value
            elif index.column() == 4:
                word.level = value
            elif index.column() == 5:
                word.audio = value
            self.dataChanged.emit()
            return True
        return False

    def get_row_data(self, row_index):
        """Retrieve a dictionary containing all data from a specific row."""
        word = self.words[row_index]
        print("here is the selectioned", word)
        if 0 <= row_index < self.rowCount():
            return Word(
                self.data(self.index(row_index, 1), Qt.DisplayRole),
                self.data(self.index(row_index, 3), Qt.DisplayRole),
                self.data(self.index(row_index, 2), Qt.DisplayRole),
                self.data(self.index(row_index, 5), Qt.DisplayRole),
                self.data(self.index(row_index, 4), Qt.DisplayRole),
                word.id if word.id else None,
            )

        else:
            return None  # Invalid row index
