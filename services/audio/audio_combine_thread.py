from PySide6.QtCore import Signal, Slot

from base import QThreadBase
from models.services import CombineAudioPayload, JobRef

from .audio_combine_worker import AudioCombineWorker


class CombineAudioThread(QThreadBase):
    updateAnkiAudio = Signal(object)
    start_combine_audio = Signal(str)
    stop_worker = Signal()
    task_complete = Signal(object, object)

    def __init__(self, job_ref: JobRef, payload: CombineAudioPayload):
        super().__init__()
        self.job_ref = job_ref
        self.payload = payload

    def run(self):
        self.worker = AudioCombineWorker(self.job_ref, self.payload)

        self.worker.moveToThread(self)
        self.worker.finished.connect(self.worker_finished)
        self.worker.task_complete.connect(self.task_complete)
        self.stop_worker.connect(self.worker.stop)
        self.worker.do_work()

    def worker_finished(self):
        self.worker.deleteLater()
        self.done.emit()

    @Slot()
    def stop(self):
        if self.isRunning():
            self.stop_worker.emit()
