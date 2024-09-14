import threading

from PySide6.QtCore import QObject, Signal

from services.network import NetworkWorker, SessionManager


class AnkiGetNoteIDsWorker(QObject):
    received_response = Signal(str, object, str)
    finished = Signal()

    def __init__(self, deckName):
        super().__init__()
        self.deckName = deckName

    def do_work(self):
        print(
            f"Starting anki get ID worker in thread: {threading.get_ident()} - {self.thread()}"
        )

        sess = SessionManager()
        json = {
            "action": "findNotes",
            "version": 6,
            "params": {"query": f'deck:"{self.deckName}"'},
        }

        net_worker = NetworkWorker(sess, "GET", "http://127.0.0.1:8765", json=json)

        net_worker.response_sig.connect(self.handle_response)
        net_worker.error_sig.connect(self.handle_response)
        net_worker.moveToThread(self.thread())
        net_worker.do_work()

    def handle_response(self, status, response, errorType=None):
        print("here", status, response)
        self.received_response.emit(status, response, errorType)
