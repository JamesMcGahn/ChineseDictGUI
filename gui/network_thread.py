import requests
from PySide6.QtCore import QObject, QThread, Signal, Slot


class NetworkWorker(QObject):
    finished = Signal()
    response_sig = Signal(str, object)
    error_sig = Signal(str, str, str)

    def __init__(self, session_mangager, operation, url, data=None, json=None):
        super().__init__()
        self.session_mangager = session_mangager
        self.url = url
        self.data = data
        self.operation = operation
        self.json = json

    @Slot()
    def do_work(self):
        try:
            if self.operation == "POST":
                response = self.session_mangager.post(self.url, data=self.data)

            elif self.operation == "SESSION":
                response = self.session_mangager.post(
                    self.url, data=self.data, json=self.json
                )
                if not any(c.name == "lang" for c in response.cookies):
                    raise requests.exceptions.RequestException

            elif self.operation == "GET":
                response = self.session_mangager.get(
                    self.url, data=self.data, json=self.json
                )

            if response.status_code in (200, 201):
                self.response_sig.emit("success", response)
            else:
                self.error_sig.emit("success", response)
                print("suc2", response)

        except requests.exceptions.ConnectionError as e:
            print("eerr")

            self.error_sig.emit("error", str(e), type(e).__name__)

        except requests.exceptions.RequestException as e:
            print("eerrs")

            self.error_sig.emit("error", str(e), type(e).__name__)

        finally:
            self.finished.emit()


class NetworkThread(QThread):
    response_sig = Signal(str, object)
    error_sig = Signal(str, str)
    finished = Signal()

    def __init__(self, session_mangager, operation, url, data=None, json=None):
        super().__init__()
        self.session_mangager = session_mangager
        self.url = url
        self.data = data
        self.operation = operation
        self.json = json

    def run(self):
        self.worker = NetworkWorker(
            self.session_mangager, self.operation, self.url, self.data, self.json
        )
        self.worker.moveToThread(self)
        self.worker.finished.connect(self.quit)
        self.worker.finished.connect(self.finished)

        self.worker.response_sig.connect(self.received_response)
        self.worker.error_sig.connect(self.received_error)
        self.worker.do_work()

    def finished(self):
        self.worker.deleteLater()
        self.finished.emit()

    def received_response(self, status, response):
        self.response_sig.emit(status, response)

    def received_error(self, status, err):
        self.error_sig.emit(status, err)
