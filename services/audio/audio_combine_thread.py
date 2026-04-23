from PySide6.QtCore import Signal, Slot

from base import QThreadBase
from models.services import JobRequest

from .audio_combine_worker import AudioCombineWorker
from .models import CombineAudioPayload


class CombineAudioThread(QThreadBase):
    updateAnkiAudio = Signal(object)
    start_combine_audio = Signal(str)
    stop_worker = Signal()
    task_complete = Signal(object)

    def __init__(self, job: JobRequest[CombineAudioPayload]):
        super().__init__()
        self.job = job

    def run(self):
        self.log_thread()
        self.worker = AudioCombineWorker(self.job)
        self.worker.moveToThread(self)
        self.worker.done.connect(self.worker_finished)
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
