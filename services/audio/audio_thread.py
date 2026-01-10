from PySide6.QtCore import QTimer, Signal, Slot

from base import QThreadBase
from models.services import AudioDownloadPayload, JobRef

from .audio_download_worker import AudioDownloadWorker


class AudioThread(QThreadBase):
    updateAnkiAudio = Signal(object)
    stop_worker = Signal()
    task_complete = Signal(object, object)
    done = Signal()

    def __init__(
        self,
        job_ref: JobRef,
        payload: AudioDownloadPayload,
        google_audio_credential="",
    ):
        super().__init__()
        self.job_ref = job_ref
        self.payload = payload
        self.google_audio_credential = google_audio_credential
        self.job_ref = job_ref

    def run(self):
        print("Starting Audio Thread")
        self.worker = AudioDownloadWorker(
            job_ref=self.job_ref,
            payload=self.payload,
            google_audio_credential=self.google_audio_credential,
        )

        self.worker.moveToThread(self)
        self.worker.task_complete.connect(self.task_complete)
        self.worker.finished.connect(self.worker_finished)
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
