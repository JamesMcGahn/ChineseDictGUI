from pathlib import Path

from PySide6.QtCore import QThread, Signal, Slot

from .whisper_worker import WhisperWorker


class WhisperThread(QThread):
    stop_worker = Signal()

    def __init__(self, folder: str, file_name: str, model_name: str = "medium"):
        super().__init__()
        self.folder = folder
        self.filename = file_name
        self.model_name = model_name

    def run(self):
        self.worker = WhisperWorker(self.folder, self.filename, self.model_name)

        self.worker.moveToThread(self)
        self.stop_worker.connect(self.worker.stop)
        self.worker.finished.connect(self.worker_finished)
        self.worker.do_work()

    @Slot()
    def stop(self):
        if self.isRunning():
            self.stop_worker.emit()

    def worker_finished(self):
        self.worker.deleteLater()
        self.wait()
        self.quit()
