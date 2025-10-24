import urllib.request
from collections import deque
from random import randint

from PySide6.QtCore import QTimer, Signal, Slot

from base import QObjectBase
from models.dictionary import Dialogue, Sentence
from utils.files import PathManager

from .google_audio_worker import GoogleAudioWorker


class AudioDownloadWorker(QObjectBase):
    updateAnkiAudio = Signal(object)
    finished = Signal()
    progress = Signal(str)
    start_whisper = Signal(str, str)

    def __init__(self, data, folder_path=None, project_name=None):
        super().__init__()
        self.folder_path = folder_path
        self.data = deque(data)
        self._stopped = False
        self.project_name = project_name
        self.queue_downloading = False
        self.count = 0
        self.data_length = len(self.data)

    def do_work(self):
        QTimer.singleShot(0, self.download_next_audio)

    def schedule_next_download(self):
        if not self.data:
            self.check_done()
        elif self._stopped:
            self.logging("Audio Download Process Stopped.", "WARN")
            self.finished.emit()
        else:
            self.count += 1
            wait_time = randint(5, 20)
            self.logging(f"Waiting {wait_time} seconds before next audio download")

            QTimer.singleShot(wait_time * 1000, self.download_next_audio)

    def check_done(self):
        if not self.data and not self.queue_downloading:
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
            elif isinstance(x, Dialogue):
                filename = x.title
            else:
                filename = x.id

            x.anki_audio = f"[sound:{filename}.mp3]"
            path = PathManager.check_dup(self.folder_path, filename, ".mp3")
            filename = PathManager.regex_path(path)["filename"]

            success_msg = f'(Lesson: {self.project_name} - {self.count+1}/{self.data_length}) Audio content written to file "{filename}.mp3"'

            if getattr(x, "audio", None):
                self.queue_downloading = True

                checkHttp = x.audio.replace("http://", "https://")

                urllib.request.urlretrieve(checkHttp, path)
                self.logging(success_msg, "INFO")

                if isinstance(x, Dialogue) and x.audio_type == "lesson":
                    self.logging("Sending Lesson File to Whisper", "INFO")
                    self.start_whisper.emit(self.folder_path, filename)
                self.queue_downloading = False
                self.updateAnkiAudio.emit(x)
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
        )

        self.google_audio.success.connect(self.google_download_success)
        self.google_audio.error.connect(self.google_download_error)
        self.google_audio.finished.connect(self.google_audio.deleteLater)
        self.google_audio.do_work()
        self.queue_downloading = True

    @Slot(object)
    def google_download_success(self, x):
        self.updateAnkiAudio.emit(x)
        self.queue_downloading = False
        self.schedule_next_download()

    @Slot()
    def google_download_error(self):
        self.queue_downloading = False
        self.schedule_next_download()

    @Slot()
    def stop(self) -> None:
        self._stopped = True
