from PySide6.QtCore import QTimer, Signal, Slot

from base import QThreadBase
from models.services import JobRequest

from .audio_download_worker import AudioDownloadWorker
from .models import AudioDownloadPayload


class AudioThread(QThreadBase):
    updateAnkiAudio = Signal(object)
    stop_worker = Signal()
    task_complete = Signal(object)
    done = Signal()

    def __init__(
        self,
        job: JobRequest[AudioDownloadPayload],
        google_audio_credential="",
    ):
        super().__init__()
        self.job = job
        self.google_audio_credential = google_audio_credential

    def run(self):
        self.log_thread()
        self.worker = AudioDownloadWorker(
            job=self.job,
            google_audio_credential=self.google_audio_credential,
        )

        self.worker.moveToThread(self)
        self.worker.task_complete.connect(self.task_complete)
        self.worker.done.connect(self.worker_finished)
        self.worker.updateAnkiAudio.connect(self.updateAnkiAudio)

        self.stop_worker.connect(self.worker.stop)
        QTimer.singleShot(0, self.worker.do_work)
        self.exec()

    def worker_finished(self):
        self.done.emit()

    @Slot()
    def stop(self):
        if self.isRunning():
            self.stop_worker.emit()
