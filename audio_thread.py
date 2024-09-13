import urllib.request
from random import randint
from time import sleep

import google
from google.cloud import texttospeech
from PySide6.QtCore import QObject, QThread, Signal, Slot

from models.dictionary import Sentence
from services import Logger
from utils import PathManager


class GoogleAudioWoker(QObject):
    success = Signal()
    error = Signal(str)

    def __init__(
        self,
        text,
        filename,
        folder_path="./",
        access_key_location="./key.json",
    ):
        super().__init__()
        self.text = text
        self.google_tried = False
        self.filename = filename
        self.folder_path = folder_path
        self.access_key_location = access_key_location

    def do_work(self):
        print("Starting Google Audio Worker...")
        print(f"google woker in thread {self.thread()}")
        try:
            client = texttospeech.TextToSpeechClient.from_service_account_json(
                self.access_key_location
            )

            input_text = texttospeech.SynthesisInput(text=self.text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="cmn-CN", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = client.synthesize_speech(
                request={
                    "input": input_text,
                    "voice": voice,
                    "audio_config": audio_config,
                }
            )

            if self.folder_path != "./":
                path = PathManager.check_dup(self.folder_path, self.filename, ".mp3")

            with open(path, "wb") as out:
                out.write(response.audio_content)
            print("wrote file")
            self.success.emit()

        # TODO: Handle File writing errors
        except google.api_core.exceptions.ServiceUnavailable as e:
            if self.google_tried is False:
                failure_msg_retry = "Failed to get Audio From Google...Trying Again..."
                Logger().insert(failure_msg_retry, "WARN")
                self.error.emit(failure_msg_retry)
                sleep(15)
                self.google_tried = True
                self.do_work(text=self.text, filename=self.filename)
            else:
                Logger().insert("Failed to get Audio From Google", "ERROR")
                Logger().insert(e, "ERROR", False)
                return False


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
                else:
                    self.filename = x.id

                x.anki_audio = f"{self.filename}.mp3"

                path = PathManager.check_dup(self.folder_path, self.filename, ".mp3")
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
                    self.gaudio = GoogleAudioWoker(
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
                gaudio = GoogleAudioWoker(
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


class AudioThread(QThread):
    updateAnkiAudio = Signal(object)

    def __init__(self, data, folder_path=None):
        super().__init__()
        self.folder_path = folder_path
        self.data = data

    def run(self):
        self.worker = AudioDownloadWorker(self.data, self.folder_path)

        self.worker.moveToThread(self)

        self.worker.finished.connect(self.worker_finished)
        self.worker.updateAnkiAudio.connect(self.updateAnkiAudio)
        self.worker.do_work()

    def worker_finished(self):
        self.worker.deleteLater()
        self.wait()
        self.quit()
        self.finished.emit()
