from pathlib import Path

from PySide6.QtCore import QTimer, Signal, Slot

from base import QThreadBase

from .open_ai_whisper_worker import OpenAIWhisperWorker
from .whisper_worker import WhisperWorker


class WhisperThread(QThreadBase):
    stop_worker = Signal()

    def __init__(self, folder: str, file_name: str, model_name: str = "medium"):
        super().__init__()
        self.folder = folder
        self.filename = file_name
        self.model_name = model_name

    def run(self):
        # self.worker = WhisperWorker(self.folder, self.filename, self.model_name) faster whisper version
        self.worker = OpenAIWhisperWorker(self.folder, self.filename, self.model_name)

        self.worker.moveToThread(self)
        self.stop_worker.connect(self.worker.stop)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.done)
        QTimer.singleShot(0, self.worker.do_work)
        self.exec()

    @Slot()
    def stop(self):
        if self.isRunning():
            self.stop_worker.emit()
