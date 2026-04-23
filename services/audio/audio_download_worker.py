import urllib.request
from collections import deque
from random import randint

from PySide6.QtCore import QTimer, Signal, Slot

from base import QWorkerBase
from base.enums import JOBSTATUS
from models.dictionary import LessonAudio
from models.services import (
    BatchJobResponse,
    JobRef,
    JobRequest,
    JobResponse,
)
from services.sentences.models import Sentence
from services.words.models import Word
from utils.files import PathManager

from .enums import AUDIOTYPE
from .google_audio_worker import GoogleAudioWorker
from .models import AudioDownloadPayload, AudioItem


class AudioDownloadWorker(QWorkerBase):
    updateAnkiAudio = Signal(object)
    progress = Signal(str)
    start_whisper = Signal(str, str)
    task_complete = Signal(object)

    def __init__(
        self,
        job: JobRequest[AudioDownloadPayload],
        google_audio_credential="",
    ):
        super().__init__()
        self.job = job
        self.folder_path = job.payload.export_path
        self.data = deque(job.payload.audio_urls)
        self._stopped = False
        self.project_name = job.payload.project_name
        self.queue_downloading = False
        self.count = 0
        self.download_success = 0
        self.download_error = 0
        self.data_length = len(self.data)
        self.project_type = ""
        self.google_audio_credential = google_audio_credential
        self.failed_items = []
        self.succeed_items = []
        self.current_item = None

    def do_work(self):
        self.log_thread()
        QTimer.singleShot(0, self.download_next_audio)

    def schedule_next_download(self):
        if not self.data:
            self.check_done()
        elif self._stopped:
            self.logging("Audio Download Process Stopped.", "WARN")
            self.done.emit()
        else:
            wait_time = randint(5, 20)
            self.logging(f"Waiting {wait_time} seconds before next audio download")

            QTimer.singleShot(wait_time * 1000, self.download_next_audio)

    def check_done(self):
        if not self.data and not self.queue_downloading:
            msg_text = (
                f"Lesson: {self.project_name} - "
                if self.project_type != "Words"
                else ""
            )
            self.logging(
                f"{msg_text}Finished Downloading {self.project_type} Audio - Success: {self.download_success} Failure: {self.download_error}"
            )

            if self.download_error == 0:
                status = JOBSTATUS.COMPLETE
            elif self.download_success == 0:
                status = JOBSTATUS.ERROR
            else:
                status = JOBSTATUS.PARTIAL_ERROR

            self.task_complete.emit(
                JobResponse(
                    job_ref=JobRef(id=self.job.id, task=self.job.task, status=status),
                    payload=BatchJobResponse(
                        success_count=self.download_success,
                        error_count=self.download_error,
                        total_count=self.data_length,
                        failed_items=self.failed_items,
                        data=self.succeed_items,
                    ),
                )
            )
            self.done.emit()

    def prepare_file_type(self, obj):
        filename = None
        if isinstance(obj, Sentence):
            filename = f"Sentence-{obj.id}"
            self.project_type = "Sentences"
        elif isinstance(obj, LessonAudio):
            filename = obj.audio_type
            self.project_type = "Lesson Audio"
        elif isinstance(obj, Word):
            filename = f"Word-{obj.id}"
            self.project_type = "Words"
        return filename

    def download_next_audio(self):
        if not self.data:
            self.check_done()
            return
        self.current_item = None

        try:
            self.current_item = None
            self.current_item = self.data.popleft()

            if self.current_item.text is None and self.current_item.source_url is None:
                self.logging("Audio Item has no text and source url.", "ERROR")
                self.download_error += 1
                self.failed_items.append(self.current_item)
                self.schedule_next_download()
                return

            path = PathManager.check_dup(
                self.current_item.target_path, self.current_item.file_name, ".mp3"
            )
            filename = PathManager.regex_path(path)["filename"]

            success_msg = f'(Lesson: {self.project_name} - {self.count + 1}/{self.data_length}) Audio content written to file "{filename}.mp3"'

            self.queue_downloading = True

            checkHttp_url = self.current_item.source_url.replace("http://", "https://")
            urllib.request.urlretrieve(checkHttp_url, path)
            self.logging(success_msg, "INFO")

            self.queue_downloading = False

            self.count += 1
            self.download_success += 1
            self.succeed_items.append(self.current_item)
            QTimer.singleShot(0, self.schedule_next_download)

        except Exception as e:

            self.queue_downloading = False
            self.logging(f"Error in Audio Download: {e}", "ERROR")
            if self.current_item.category != AUDIOTYPE.DEFAULT:
                error_msg = "Something went wrong...Trying to Get Audio from Google..."
                success_msg = f'(Lesson: {self.project_name} - {self.count + 1}/{self.data_length}) Audio content written to file "{filename}.mp3"'
                self.logging(error_msg, "ERROR")
                self.start_google_download(self.current_item, filename, success_msg)
            else:
                self.download_error += 1
                QTimer.singleShot(0, self.schedule_next_download)

    def start_google_download(self, x: AudioItem, filename, success_message):
        self.google_audio = GoogleAudioWorker(
            text=x.text,
            filename=x.file_name,
            folder_path=x.target_path,
            project_name=self.project_name,
            success_message=success_message,
            audio_object=x,
            google_audio_credential=self.google_audio_credential,
        )
        self.google_audio.success.connect(self.google_download_success)
        self.google_audio.error.connect(self.google_download_error)
        self.google_audio.done.connect(self.google_audio.deleteLater)
        self.google_audio.do_work()
        self.queue_downloading = True

    @Slot(object)
    def google_download_success(self, x):
        self.count += 1
        self.download_success += 1
        # self.updateAnkiAudio.emit(x)
        self.queue_downloading = False
        self.succeed_items.append(x)
        QTimer.singleShot(0, self.schedule_next_download)

    @Slot()
    def google_download_error(self):
        self.logging("Failed Reattempt with Google Audio Download. Skipping", "WARN")
        self.download_error += 1
        self.queue_downloading = False
        self.failed_items.append(self.current_item)
        QTimer.singleShot(0, self.schedule_next_download)

    @Slot()
    def stop(self) -> None:
        self._stopped = True
