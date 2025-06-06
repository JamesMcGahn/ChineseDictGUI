import threading

from PySide6.QtCore import QObject, Signal, Slot

from db import DatabaseManager
from db.dals import SentsDAL, WordsDAL


class FindAnkiIDsInLocalWorker(QObject):
    ids_not_in_local = Signal(list)

    finished = Signal()

    def __init__(self, ankiIds, dtype="words"):
        super().__init__()
        self.db_manager = DatabaseManager("chineseDict.db")
        self.ankiIds = ankiIds
        self.dtype = dtype

    @Slot()
    def do_work(self):
        print(
            f"Find Anki Ids in Local running in thread: {threading.get_ident()} - {self.thread()}"
        )
        self.db_manager.connect()

        no_db_matches = []

        if self.dtype == "words":
            print("here")
            wd = WordsDAL(self.db_manager)
            result = wd.get_words_all_anki_ids()
            print(result, "aaa")

        else:
            sd = SentsDAL(self.db_manager)
            result = sd.get_sentence_all_anki_ids()

        result = result.fetchall()

        local_anki_ids = [word[0] for word in result]
        no_db_matches = [id for id in self.ankiIds if id not in local_anki_ids]
        print(f"There are {len(no_db_matches)} missing Ids")

        self.db_manager.disconnect()
        self.ids_not_in_local.emit(no_db_matches)
        self.finished.emit()
