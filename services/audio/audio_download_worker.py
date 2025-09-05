import urllib.request
from random import randint
from time import sleep

from PySide6.QtCore import Signal, Slot

from base import QObjectBase
from models.dictionary import Dialogue, Sentence
from services import Logger
from utils.files import PathManager

from .google_audio_worker import GoogleAudioWorker


class AudioDownloadWorker(QObjectBase):
    updateAnkiAudio = Signal(object)
    finished = Signal()
    progress = Signal(str)
    start_whisper = Signal(str, str)

    def __init__(self, data, folder_path=None):
        super().__init__()
        self.folder_path = folder_path
        self.data = data
        self._stopped = False

    def do_work(self):
        for i, x in enumerate(self.data):
            if self._stopped:
                self.logging("Audio Download Process Stopped.", "WARN")
                self.finished.emit()
                return

            try:
                if isinstance(x, Sentence):
                    self.filename = f"10KS-{x.id}"
                elif isinstance(x, Dialogue):
                    self.filename = x.title
                else:
                    self.filename = x.id

                x.anki_audio = f"[sound:{self.filename}.mp3]"

                path = PathManager.check_dup(self.folder_path, self.filename, ".mp3")
                self.filename = PathManager.regex_path(path)["filename"]
                msg = f'({i+1}/{len(self.data)}) Audio content written to file "{self.filename}.mp3"'

                if x.audio:
                    checkHttp = x.audio.replace("http://", "https://")
                    urllib.request.urlretrieve(checkHttp, path)

                    self.logging(
                        msg,
                        "INFO",
                    )

                    if isinstance(x, Dialogue) and x.audio_type == "lesson":

                        self.logging(
                            "Sending File to Whisper",
                            "INFO",
                        )
                        self.start_whisper.emit(self.folder_path, self.filename)

                    self.updateAnkiAudio.emit(x)
                else:
                    self.logging("There is not an audio link for the file", "WARN")
                    if isinstance(x, Dialogue):
                        self.logging(f"There is not an audio link for {x.audio_type}")
                        continue
                    self.gaudio = GoogleAudioWorker(
                        text=x.chinese,
                        filename=self.filename,
                        folder_path=self.folder_path,
                    )

                    self.gaudio.moveToThread(self.thread())

                    self.gaudio.success.connect(
                        lambda x=x, msg=msg: self.updateGoogleAnkiAudio(
                            x,
                            msg,
                        )
                    )
                    self.gaudio.error.connect(self.google_audio_error)
                    self.gaudio.do_work()
            except Exception as e:
                Logger().insert(e, "ERROR", False)
                msg = "Something went wrong...Trying to Get Audio from Google..."
                Logger().insert(
                    "Something went wrong...Trying to Get Audio from Google...", "ERROR"
                )
                self.progress.emit(msg)
                gaudio = GoogleAudioWorker(
                    text=x.chinese, filename=self.filename, folder_path=self.folder_path
                )

                gaudio.moveToThread(self.thread())

                gaudio.success.connect(
                    lambda x=x, msg=msg: self.updateGoogleAnkiAudio(
                        x,
                        msg,
                    )
                )
                gaudio.error.connect(self.google_audio_error)
                gaudio.finished.connect(gaudio.deleteLater)
                gaudio.do_work()
            sleep(randint(5, 15))
        self.finished.emit()

    @Slot(object, str)
    def updateGoogleAnkiAudio(self, x, msg):
        Logger().insert(
            msg,
            "INFO",
        )
        self.progress.emit(msg)
        self.updateAnkiAudio.emit(x)

    @Slot(str)
    def google_audio_error(self, msg):
        self.progress.emit(msg)

    @Slot()
    def stop(self) -> None:
        self._stopped = True
