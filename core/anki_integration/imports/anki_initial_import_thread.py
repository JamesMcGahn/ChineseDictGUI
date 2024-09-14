import threading
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QThread, Signal

from db import DatabaseManager
from db.workers import SentsQueryWorker, WordsQueryWorker
from models.dictionary import Sentence, Word

from .anki_find_id_inlocal_worker import FindAnkiIDsInLocalWorker
from .anki_get_ids_worker import AnkiGetNoteIDsWorker
from .anki_get_note_info_worker import AnkiGetNoteInfoWorker


class AnkiInitialImportThread(QThread):
    finished = Signal()

    def __init__(self, deckName, dtype="words"):
        super().__init__()
        self.dtype = dtype
        self.deckName = deckName

    def run(self):
        print(
            f"Starting Anki Initial Import Thread: {threading.get_ident()} - {self.thread()}"
        )
        self.noteIDWorker = AnkiGetNoteIDsWorker(self.deckName)
        self.noteIDWorker.moveToThread(self.thread())
        self.noteIDWorker.received_response.connect(self.received_response)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.executor.submit(self.noteIDWorker.do_work)

    def received_response(self, status, response, errorType=None):
        if status == "error":
            print(status, response, errorType)
        else:
            ankiIds = response.json()["result"]
            # print(ankiIds)
            db = DatabaseManager("chineseDict.db")
            self.worker = FindAnkiIDsInLocalWorker(db, ankiIds, dtype=self.dtype)
            self.worker.moveToThread(self)
            self.worker.ids_not_in_local.connect(self.ids_not_found)

            # self.worker.do_work

            self.executor.submit(self.worker.do_work)
            # anki worker here

    def ids_not_found(self, ids: list):
        if ids:
            self.get_noteinfo_worker = AnkiGetNoteInfoWorker(ids, dtype=self.dtype)
            self.get_noteinfo_worker.response_sig.connect(self.notes_response)
            self.get_noteinfo_worker.moveToThread(self.thread())
            self.executor.submit(self.get_noteinfo_worker.do_work)
        else:
            print("All IDs found in local database")
            self.finished.emit()

    def notes_response(self, status, response, errorType=None):
        db = DatabaseManager("chineseDict.db")

        if status == "success" and response is None:
            print("Nothing to add")
            self.finished.emit()
            return

        if self.dtype == "words":
            words = [
                Word(
                    chinese=word["fields"]["中文"]["value"],
                    pinyin=word["fields"]["Pinyin"]["value"],
                    definition=word["fields"]["English"]["value"],
                    audio=None,
                    level=word["fields"]["Notes"]["value"],
                    anki_audio=word["fields"]["audio"]["value"],
                    anki_id=word["noteId"],
                    anki_update=word["mod"],
                )
                for word in response["result"]
            ]
            self.dbworker = WordsQueryWorker(
                db,
                "insert_words",
                words=words,
            )
        else:
            sents = [
                Sentence(
                    chinese=sent["fields"]["中文"]["value"],
                    pinyin=sent["fields"]["Pinyin"]["value"],
                    english=sent["fields"]["English"]["value"],
                    audio=None,
                    level=sent["fields"]["Notes"]["value"],
                    anki_audio=sent["fields"]["audio"]["value"],
                    anki_id=sent["noteId"],
                    anki_update=sent["mod"],
                )
                for sent in response["result"]
            ]
            self.dbworker = SentsQueryWorker(
                db,
                "insert_sentences",
                sentences=sents,
            )

        self.dbworker.moveToThread(self)
        self.dbworker.do_work()
        self.dbworker.finished.connect(self.quit)
        self.dbworker.error_occurred.emit(self.error_occured)
        self.dbworker.finished.connect(self.dbworker.deleteLater)
        self.finished.emit()

    def error_occured(self, message):
        print(message)

    def update_db_integration_record(self):
        pass
        # TODO: update integration table with initial_import_done
