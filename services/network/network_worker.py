import threading

import requests
from PySide6.QtCore import QObject, QThread, Signal, Slot


class NetworkWorker(QObject):
    finished = Signal()
    response_sig = Signal(str, object)
    error_sig = Signal(str, str, str)
    start_work = Signal()

    def __init__(
        self, session_mangager, operation, url, data=None, json=None, timeout=10
    ):
        super().__init__()
        self.session_mangager = session_mangager
        self.url = url
        self.data = data
        self.operation = operation
        self.json = json
        self.timeout = timeout
        self.start_work.connect(self.do_work)

    @Slot()
    def do_work(self):
        print(
            f"Starting NetworkWorker in thread: {threading.get_ident()} - {self.thread()}"
        )

        try:
            if self.operation == "POST":
                response = self.session_mangager.post(
                    self.url, data=self.data, timeout=self.timeout
                )

            elif self.operation == "SESSION":
                response = self.session_mangager.post(
                    self.url, data=self.data, json=self.json, timeout=self.timeout
                )
                if not any(c.name == "lang" for c in response.cookies):
                    raise requests.exceptions.RequestException

            elif self.operation == "GET":
                print("here")
                response = self.session_mangager.get(
                    self.url, data=self.data, json=self.json, timeout=self.timeout
                )

            if response.status_code in (200, 201):
                self.response_sig.emit("success", response)
                print("suc1", response.json())

            else:
                self.error_sig.emit("success", response)
                print("suc2", response.json())

        except requests.exceptions.ConnectionError as e:
            # TODO - handle error
            print(e)
            self.error_sig.emit("error", str(e), type(e).__name__)

        except requests.exceptions.RequestException as e:
            print(e)
            # TODO - handle error

            self.error_sig.emit("error", str(e), type(e).__name__)

        finally:
            self.finished.emit()
