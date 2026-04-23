from time import time

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal

from services.words.models import Word


class WordTableModel(QAbstractTableModel):
    dataChanged = Signal()
    wordUpdated = Signal(object)

    def __init__(self, words=None):
        super().__init__()
        self.words = words if words is not None else []

    def current_timestamp(self):
        return int(time())

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
                return "English"
            if section == 4:
                return "Level"
            if section == 5:
                return "Audio Link"

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
                return word.english
            elif index.column() == 4:
                return word.level
            elif index.column() == 5:
                return word.audio_link
        elif role == Qt.EditRole:
            if index.column() == 1:
                return word.chinese
            elif index.column() == 2:
                return word.pinyin
            elif index.column() == 3:
                return word.english
            elif index.column() == 4:
                return word.level
            elif index.column() == 5:
                return word.audio_link

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
                word.english = value
            elif index.column() == 4:
                word.level = value
            elif index.column() == 5:
                word.audio_link = value
            word.local_update = self.current_timestamp()
            self.dataChanged.emit()
            self.wordUpdated.emit(word)
            return True
        return False

    def get_row_data(self, row_index):
        """Retrieve a dictionary containing all data from a specific row."""
        word = self.words[row_index]
        print("here is the selectioned", word)
        if 0 <= row_index < self.rowCount():
            return Word(
                chinese=self.data(self.index(row_index, 1), Qt.DisplayRole),
                english=self.data(self.index(row_index, 3), Qt.DisplayRole),
                pinyin=self.data(self.index(row_index, 2), Qt.DisplayRole),
                audio_link=self.data(self.index(row_index, 5), Qt.DisplayRole),
                level=self.data(self.index(row_index, 4), Qt.DisplayRole),
                id=word.id if word.id else None,
                anki_audio=word.anki_audio,
                anki_id=word.anki_id,
                anki_update=word.anki_update,
                local_update=word.local_update,
                lesson=word.lesson,
                runtime_id=word.runtime_id,
                staging_path=word.staging_path,
                storage_path=word.storage_path,
            )

        else:
            return None  # Invalid row index
