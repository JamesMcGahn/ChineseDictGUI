import urllib.request
from collections import deque
from random import randint

from PySide6.QtCore import QTimer, Signal, Slot

from base import QWorkerBase
from base.enums import JOBSTATUS
from models.dictionary import LessonAudio, Sentence, Word
from models.services import AudioDownloadPayload, JobItem, JobRef
from utils.files import PathManager

from .google_audio_worker import GoogleAudioWorker


class AudioDownloadWorker(QWorkerBase):
    updateAnkiAudio = Signal(object)
    progress = Signal(str)
    start_whisper = Signal(str, str)
    task_complete = Signal(object, object)

    def __init__(
        self,
        job: JobItem[AudioDownloadPayload],
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

    def do_work(self):
        self.log_thread()
        QTimer.singleShot(0, self.download_next_audio)

    def schedule_next_download(self):
        if not self.data:
            self.check_done()
        elif self._stopped:
            self.logging("Audio Download Process Stopped.", "WARN")
            self.finished.emit()
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

            self.task_complete.emit(
                JobRef(
                    id=self.job.id,
                    task=self.job.task,
                    status=(
                        JOBSTATUS.COMPLETE
                        if self.download_error == 0
                        else JOBSTATUS.ERROR
                    ),
                ),
                {
                    "success": self.download_success,
                    "failure": self.download_error,
                    "total": self.data_length,
                },
            )
            self.finished.emit()

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
        x = None

        try:
            x = self.data.popleft()
            filename = self.prepare_file_type(x)
            if filename is None:
                self.logging("Non supported Audio Download object type", "ERROR")
                self.download_error += 1
                self.schedule_next_download()
                return

            path = PathManager.check_dup(self.folder_path, filename, ".mp3")
            filename = PathManager.regex_path(path)["filename"]
            if not isinstance(x, LessonAudio):
                x.anki_audio = f"[sound:{filename}.mp3]"
            success_msg = f'(Lesson: {self.project_name} - {self.count + 1}/{self.data_length}) Audio content written to file "{filename}.mp3"'

            if getattr(x, "audio", None):
                self.queue_downloading = True

                checkHttp = x.audio.replace("http://", "https://")

                urllib.request.urlretrieve(checkHttp, path)
                self.logging(success_msg, "INFO")

                self.queue_downloading = False

                if not isinstance(x, LessonAudio):
                    self.updateAnkiAudio.emit(x)

                self.count += 1
                self.download_success += 1
                QTimer.singleShot(0, self.schedule_next_download)
            else:
                self.logging("There is not an audio link for the file", "WARN")
                if isinstance(x, LessonAudio):
                    self.logging(f"There is not an audio link for {x.audio_type}")
                    self.schedule_next_download()
                else:
                    self.start_google_download(x, filename, success_msg)

        except Exception as e:

            self.queue_downloading = False
            self.logging(f"Error in Audio Download: {e}", "ERROR")
            if isinstance(x, (Sentence, Word)):
                error_msg = "Something went wrong...Trying to Get Audio from Google..."
                success_msg = f'(Lesson: {self.project_name} - {self.count + 1}/{self.data_length}) Audio content written to file "{filename}.mp3"'
                self.logging(error_msg, "ERROR")
                self.start_google_download(x, filename, success_msg)
            else:
                self.download_error += 1
                QTimer.singleShot(0, self.schedule_next_download)

    def start_google_download(self, x, filename, success_message):
        self.google_audio = GoogleAudioWorker(
            text=x.chinese,
            filename=filename,
            folder_path=self.folder_path,
            project_name=self.project_name,
            success_message=success_message,
            audio_object=x,
            google_audio_credential=self.google_audio_credential,
        )
        self.google_audio.success.connect(self.google_download_success)
        self.google_audio.error.connect(self.google_download_error)
        self.google_audio.finished.connect(self.google_audio.deleteLater)
        self.google_audio.do_work()
        self.queue_downloading = True

    @Slot(object)
    def google_download_success(self, x):
        self.count += 1
        self.download_success += 1
        self.updateAnkiAudio.emit(x)
        self.queue_downloading = False
        QTimer.singleShot(0, self.schedule_next_download)

    @Slot()
    def google_download_error(self):
        self.logging("Failed Reattempt with Google Audio Download. Skipping", "WARN")
        self.download_error += 1
        self.queue_downloading = False
        QTimer.singleShot(0, self.schedule_next_download)

    @Slot()
    def stop(self) -> None:
        self._stopped = True
