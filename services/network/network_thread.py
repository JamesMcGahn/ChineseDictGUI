from PySide6.QtCore import Signal

from base import QThreadBase

from .network_worker import NetworkWorker


class NetworkThread(QThreadBase):
    response_sig = Signal(str, object)
    error_sig = Signal(str, str, str)

    def __init__(self, operation, url, data=None, json=None):
        super().__init__()
        self.url = url
        self.data = data
        self.operation = operation
        self.json = json

    def run(self):
        self.worker = NetworkWorker(self.operation, self.url, self.data, self.json)
        self.worker.moveToThread(self)
        self.worker.finished.connect(self.quit)
        self.worker.finished.connect(self.worker_finished)

        self.worker.response_sig.connect(self.received_response)
        self.worker.error_sig.connect(self.received_error)
        self.worker.do_work()

    def worker_finished(self):
        self.worker.deleteLater()
        self.done.emit()

    def received_response(self, status, response):
        self.response_sig.emit(status, response)

    def received_error(self, status, err, errType):
        self.error_sig.emit(status, err, errType)
