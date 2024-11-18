import threading

from PySide6.QtCore import QObject, Signal, Slot

from services.network import NetworkWorker, SessionManager


class AnkiGetNoteInfoWorker(QObject):
    response_sig = Signal(str, object, str)

    finished = Signal()

    def __init__(self, ankiIds, dtype="words"):
        super().__init__()
        self.ankiIds = ankiIds
        self.dtype = dtype

    @Slot()
    def do_work(self):
        print(
            f"Starting Anki Note Info worker in thread: {threading.get_ident()} - {self.thread()}"
        )

        json = {
            "action": "notesInfo",
            "version": 6,
            "params": {"notes": self.ankiIds},
        }

        if len(self.ankiIds) == 0:
            self.response_sig.emit("success", None, None)
            self.finished.emit()
            return
        print("Start")
        sess = SessionManager()
        self.net_worker = NetworkWorker(
            sess, "GET", "http://127.0.0.1:8765", json=json, timeout=60
        )
        self.net_worker.moveToThread(self.thread())
        self.net_worker.response_sig.connect(self.notes_response)
        self.net_worker.error_sig.connect(self.notes_response)

        self.net_worker.do_work()

    @Slot(str, object, str)
    def notes_response(self, status, response, errorType=None):
        print("here - ttt")
        res = response
        error = res.json()["error"]
        if status == "error" or error is not None:
            print(status, response, errorType)
            self.response_sig.emit("error", error, error)
        else:
            print(res)
            self.response_sig.emit(status, res.json(), errorType)

        self.finished.emit()
