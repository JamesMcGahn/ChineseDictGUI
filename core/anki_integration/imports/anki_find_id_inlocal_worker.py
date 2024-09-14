import threading

from PySide6.QtCore import QObject, Signal, Slot

from db.dals import SentsDAL, WordsDAL


class FindAnkiIDsInLocalWorker(QObject):
    ids_not_in_local = Signal(list)

    finished = Signal()

    def __init__(self, db_manager, ankiIds, dtype="words"):
        super().__init__()
        self.db_manager = db_manager
        self.ankiIds = ankiIds
        self.dtype = dtype

    @Slot()
    def do_work(self):
        print(
            f"Find Anki Ids in Local running in thread: {threading.get_ident()} - {self.thread()}"
        )

        self.db_manager.connect()

        no_db_matches = []

        for id in self.ankiIds:
            if self.dtype == "words":
                wd = WordsDAL(self.db_manager)
                result = wd.get_word_by_ankiid(id)
            else:
                sd = SentsDAL(self.db_manager)
                result = sd.get_sentence_by_ankiid(id)

            if result.fetchone() is None:
                no_db_matches.append(id)

        self.db_manager.disconnect()
        self.ids_not_in_local.emit(no_db_matches)
