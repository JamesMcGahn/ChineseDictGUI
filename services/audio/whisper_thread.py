from pathlib import Path

from PySide6.QtCore import QThread, Signal

from .whisper_worker import WhisperWorker


class WhisperThread(QThread):
    finished = Signal()

    def __init__(self, folder: str, file_name: str, model_name: str = "medium"):
        super().__init__()
        self.folder = folder
        self.filename = file_name
        self.model_name = model_name

    def run(self):
        self.worker = WhisperWorker(self.folder, self.filename, self.model_name)

        self.worker.moveToThread(self)

        self.worker.finished.connect(self.worker_finished)
        self.worker.do_work()
        print("IN whisper thread")

    def worker_finished(self):
        self.worker.deleteLater()
        self.wait()
        self.quit()
        self.finished.emit()
