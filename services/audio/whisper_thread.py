from pathlib import Path

from PySide6.QtCore import QTimer, Signal, Slot

from base import QThreadBase
from base.enums import WHISPERPROVIDER
from models.services import JobRef, WhisperPayload

from .faster_whisper_worker import FasterWhisperWorker
from .open_ai_whisper_worker import OpenAIWhisperWorker


class WhisperThread(QThreadBase):
    stop_worker = Signal()
    task_complete = Signal(object, object)

    def __init__(self, job_ref: JobRef, payload: WhisperPayload):
        super().__init__()
        self.job_ref = job_ref
        self.payload = payload

    def run(self):
        if self.payload.provider == WHISPERPROVIDER.FASTER_WHISPER:
            self.worker = FasterWhisperWorker(
                job_ref=self.job_ref, payload=self.payload
            )
        elif self.payload.provider == WHISPERPROVIDER.WHISPER:
            self.worker = OpenAIWhisperWorker(
                job_ref=self.job_ref, payload=self.payload
            )
        else:
            self.logging("Incorrect Whisper Provider selected. Ending Thread", "WARN")
            self.done.emit()
            return

        self.worker.moveToThread(self)
        self.stop_worker.connect(self.worker.stop)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.done)
        self.worker.task_complete.connect(self.task_complete)
        QTimer.singleShot(0, self.worker.do_work)
        self.exec()

    @Slot()
    def stop(self):
        if self.isRunning():
            self.stop_worker.emit()
