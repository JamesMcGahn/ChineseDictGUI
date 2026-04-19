from pathlib import Path

from PySide6.QtCore import QTimer, Signal, Slot

from base import QThreadBase
from models.services import JobRequest

from .enums import WHISPERPROVIDER
from .faster_whisper_worker import FasterWhisperWorker
from .models import WhisperPayload
from .open_ai_whisper_worker import OpenAIWhisperWorker


class WhisperThread(QThreadBase):
    stop_worker = Signal()
    task_complete = Signal(object)

    def __init__(self, job: JobRequest[WhisperPayload]):
        super().__init__()
        self.job = job

    def run(self):
        self.log_thread()
        if self.job.payload.provider == WHISPERPROVIDER.FASTER_WHISPER:
            self.worker = FasterWhisperWorker(job=self.job)
        elif self.job.payload.provider == WHISPERPROVIDER.WHISPER:
            self.worker = OpenAIWhisperWorker(job=self.job)
        else:
            self.logging("Incorrect Whisper Provider selected. Ending Thread", "WARN")
            self.done.emit()
            return

        self.worker.moveToThread(self)
        self.stop_worker.connect(self.worker.stop)
        self.worker.done.connect(self.worker.deleteLater)
        self.worker.done.connect(self.done)
        self.worker.task_complete.connect(self.task_complete)
        QTimer.singleShot(0, self.worker.do_work)
        self.exec()

    @Slot()
    def stop(self):
        if self.isRunning():
            self.stop_worker.emit()
