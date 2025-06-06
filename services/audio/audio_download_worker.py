import urllib.request
from random import randint
from time import sleep

from PySide6.QtCore import QObject, Signal, Slot

from models.dictionary import Dialogue, Sentence
from services import Logger
from utils.files import PathManager

from .google_audio_worker import GoogleAudioWorker


class AudioDownloadWorker(QObject):
    updateAnkiAudio = Signal(object)
    finished = Signal()
    progress = Signal(str)

    def __init__(self, data, folder_path=None):
        super().__init__()
        self.folder_path = folder_path
        self.data = data

    def do_work(self):
        for i, x in enumerate(self.data):
            print(x)
            print(x.audio)
            print(f"audio woker in thread {self.thread()}")

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

                    Logger().insert(
                        msg,
                        "INFO",
                    )
                    self.updateAnkiAudio.emit(x)
                else:
                    print("no audio link")
                    if isinstance(x, Dialogue):
                        print(f"There is not an audio link for {x.audio_type}")
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
                gaudio.do_work()
            sleep(randint(5, 15))
        self.finished.emit()

    @Slot(object, str)
    def updateGoogleAnkiAudio(self, x, msg):
        print("received audio from Google", x, msg)
        Logger().insert(
            msg,
            "INFO",
        )
        self.progress.emit(msg)
        self.updateAnkiAudio.emit(x)

    @Slot(str)
    def google_audio_error(self, msg):
        self.progress.emit(msg)
