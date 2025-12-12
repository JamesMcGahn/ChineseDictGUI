import urllib.request
from collections import deque
from random import randint

from PySide6.QtCore import QTimer, Signal, Slot

from base import QWorkerBase
from models.dictionary import Dialogue, Sentence
from utils.files import PathManager

from .google_audio_worker import GoogleAudioWorker


class AudioDownloadWorker(QWorkerBase):
    updateAnkiAudio = Signal(object)
    finished = Signal()
    progress = Signal(str)
    start_whisper = Signal(str, str)

    def __init__(
        self, data, folder_path=None, project_name=None, google_audio_credential=""
    ):
        super().__init__()
        self.folder_path = folder_path
        self.data = deque(data)
        self._stopped = False
        self.project_name = project_name
        self.queue_downloading = False
        self.count = 1
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
            self.finished.emit()

    def download_next_audio(self):
        if not self.data:
            self.check_done()
            return
        try:
            x = self.data.popleft()
            filename = ""
            if isinstance(x, Sentence):
                filename = f"10KS-{x.id}"
                self.project_type = "Sentences"
            elif isinstance(x, Dialogue):
                filename = x.title
                self.project_type = "Dialogue"
            else:
                filename = x.id
                self.project_type = "Words"

            x.anki_audio = f"[sound:{filename}.mp3]"
            path = PathManager.check_dup(self.folder_path, filename, ".mp3")
            filename = PathManager.regex_path(path)["filename"]

            success_msg = f'(Lesson: {self.project_name} - {self.count}/{self.data_length}) Audio content written to file "{filename}.mp3"'

            if getattr(x, "audio", None):
                self.queue_downloading = True

                checkHttp = x.audio.replace("http://", "https://")

                urllib.request.urlretrieve(checkHttp, path)
                self.logging(success_msg, "INFO")

                if (
                    isinstance(x, Dialogue)
                    and x.audio_type == "lesson"
                    and x.transcribe
                ):
                    self.logging("Sending Lesson File to Whisper", "INFO")
                    self.start_whisper.emit(self.folder_path, filename)
                self.queue_downloading = False
                self.updateAnkiAudio.emit(x)
                self.count += 1
                self.download_success += 1
                self.schedule_next_download()

            else:
                self.logging("There is not an audio link for the file", "WARN")
                if isinstance(x, Dialogue):
                    self.logging(f"There is not an audio link for {x.audio_type}")
                    self.schedule_next_download()
                else:
                    self.start_google_download(x, filename, success_msg)

        except Exception as e:
            self.queue_downloading = False
            self.logging(f"Error in Audio Download: {e}", "ERROR")
            error_msg = "Something went wrong...Trying to Get Audio from Google..."
            self.logging(error_msg, "ERROR")
            self.start_google_download(x, filename, success_msg)

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
        self.schedule_next_download()

    @Slot()
    def google_download_error(self):
        self.download_error += 1
        self.queue_downloading = False
        self.schedule_next_download()

    @Slot()
    def stop(self) -> None:
        self._stopped = True
