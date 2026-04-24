from functools import partial

from PySide6.QtCore import QTimer, Signal, Slot

from base import QThreadBase
from models.services import JobRequest

from .audio_download_google import GoogleAudioDownload
from .audio_download_http import HTTPAudioDownload
from .base import BaseAudioDLProvider
from .enums import AUDIODLPROVIDER
from .models import AudioDownloadPayload


class AudioThread(QThreadBase):
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

        self.handlers: dict[AUDIODLPROVIDER.HTTP, BaseAudioDLProvider] = {
            AUDIODLPROVIDER.HTTP: HTTPAudioDownload,
            AUDIODLPROVIDER.GOOGLE: partial(
                GoogleAudioDownload,
                google_audio_credential=self.google_audio_credential,
            ),
        }

    def run(self):
        self.log_thread()
        provider = self.job.payload.provider
        factory = self.handlers.get(provider)
        if not factory:
            self.logging(f"Could not find a provider for {provider}", "ERROR")
            self.worker_finished()
            return

        self.worker = factory(self.job)
        self.worker.moveToThread(self)
        self.worker.task_complete.connect(self.task_complete)
        self.worker.done.connect(self.worker_finished)

        self.stop_worker.connect(self.worker.stop)
        QTimer.singleShot(0, self.worker.do_work)
        self.exec()

    def worker_finished(self):
        self.done.emit()

    @Slot()
    def stop(self):
        if self.isRunning():
            self.stop_worker.emit()
