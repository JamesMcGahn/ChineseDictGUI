import threading
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QObject, QThread, Signal, Slot

from db.dals import SentsDAL, WordsDAL
from db.db_manager import DatabaseManager
from db_query_worker import DBQueryWorker
from models.dictionary import Sentence, Word
from network_thread import NetworkWorker
from session_manager import SessionManger


class FindAnkiInLocal(QObject):
    response_sig = Signal(str, object, str)

    finished = Signal()

    def __init__(self, db_manager, ankiIds, dtype="words"):
        super().__init__()
        self.db_manager = db_manager
        self.ankiIds = ankiIds
        self.dtype = dtype

    @Slot()
    def do_work(self):
        print(f"Current thread ID -- find: {threading.get_ident()}")
        print(f"Anki running in thread: {QThread.currentThread()}")
        self.db_manager.connect()
        wd = WordsDAL(self.db_manager)
        sd = SentsDAL(self.db_manager)

        no_db_matches = []

        for id in self.ankiIds:
            if self.dtype == "words":
                result = wd.get_word_by_ankiid(id)
            else:
                result = sd.get_sentence_by_ankiid(id)

            if result.fetchone() is None:
                no_db_matches.append(id)

        self.db_manager.disconnect()

        json = {
            "action": "notesInfo",
            "version": 6,
            "params": {"notes": no_db_matches},
        }

        if len(no_db_matches) == 0:
            self.response_sig.emit("success", None, None)
            self.finished.emit()
            return

        sess = SessionManger()
        self.net_worker = NetworkWorker(
            sess, "GET", "http://127.0.0.1:8765", json=json, timeout=60
        )
        self.net_worker.moveToThread(self.thread())
        self.net_worker.response_sig.connect(self.notes_response)
        self.net_worker.error_sig.connect(self.notes_response)

        self.net_worker.do_work()

    @Slot(str, object, str)
    def notes_response(self, status, response, errorType=None):
        res = response
        if status == "error" or res.json()["error"] is not None:
            print(status, response, errorType)
            self.response_sig.emit(status, None, errorType)
        else:
            print(res)
            self.response_sig.emit(status, res.json(), errorType)

        self.finished.emit()


class AnkiImportThread(QThread):
    finished = Signal()

    def __init__(self, dname, dtype="words"):
        super().__init__()
        self.dtype = dtype
        self.dname = dname

    def run(self):
        sess = SessionManger()
        json = {
            "action": "findNotes",
            "version": 6,
            "params": {"query": f'deck:"{self.dname}"'},
        }

        net_worker = NetworkWorker(sess, "GET", "http://127.0.0.1:8765", json=json)

        net_worker.response_sig.connect(self.received_response)
        net_worker.error_sig.connect(self.received_response)
        net_worker.moveToThread(self.thread())

        self.executor = ThreadPoolExecutor(max_workers=4)
        self.executor.submit(net_worker.do_work)

    def received_response(self, status, response, errorType=None):
        if status == "error":
            print(status, response, errorType)
        else:
            ankiIds = response.json()["result"]
            print(ankiIds)
            db = DatabaseManager("chineseDict.db")
            self.worker = FindAnkiInLocal(db, ankiIds, dtype=self.dtype)
            self.worker.moveToThread(self.thread())
            self.worker.response_sig.connect(self.notes_response)

            # self.worker.do_work

            self.executor.submit(self.worker.do_work)
            # anki worker here

    def notes_response(self, status, response, errorType=None):
        print("here")
        db = DatabaseManager("chineseDict.db")
        print("ss", response)

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
            self.dbworker = DBQueryWorker(
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
            self.dbworker = DBQueryWorker(
                db,
                "insert_sentences",
                sentences=sents,
            )

        self.dbworker.moveToThread(self.thread())
        self.dbworker.do_work()
        self.dbworker.finished.connect(self.quit)
        self.dbworker.error_occurred.emit(self.error_occured)
        self.dbworker.finished.connect(self.dbworker.deleteLater)
        self.finished.emit()

    def error_occured(self, message):
        print(message)
