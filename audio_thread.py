import urllib.request
from random import randint
from time import sleep

import google
from google.cloud import texttospeech
from PySide6.QtCore import QThread, Signal

from models.dictionary import Sentence
from services import Logger
from utils import PathManager


class AudioThread(QThread):
    updateAnkiAudio = Signal(object)

    def __init__(self, data, folder_path=None):
        super().__init__()
        self.folder_path = folder_path
        self.data = data

    def google_audio(
        self,
        text,
        filename,
    ):
        try:
            client = texttospeech.TextToSpeechClient.from_service_account_json(
                "./key.json"
            )

            input_text = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="cmn-CN",
                name="cmn-CN-Standard-D",
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

            if self.folder_path is not None:
                path = PathManager.check_dup(self.folder_path, filename, ".mp3")
            else:
                path = "./"

            with open(path, "wb") as out:
                out.write(response.audio_content)
                return True
        except google.api_core.exceptions.ServiceUnavailable as e:
            if self.google_tried is False:
                Logger().insert(
                    "Failed to get Audio From Google...Trying Again...", "WARN"
                )
                sleep(15)
                self.google_tried = True
                self.google_audio(text, filename)
            else:
                Logger().insert("Failed to get Audio From Google", "ERROR")
                Logger().insert(e, "ERROR", False)
                return False

    def run(self):
        for i, x in enumerate(self.data):
            print(x)
            print(x.audio)
            try:
                filename = x.id

                if isinstance(x, Sentence):
                    filename = f"10KS-{x.id}"

                x.anki_audio = f"{filename}.mp3"

                if not x.audio and isinstance(x, Sentence):
                    success = self.google_audio(x.chinese, filename)
                    if success:
                        pass  # TODO notify user / logger
                    continue

                path = PathManager.check_dup(self.folder_path, filename, ".mp3")

                checkHttp = x.audio.replace("http://", "https://")
                urllib.request.urlretrieve(checkHttp, path)
                Logger().insert(
                    f'({i+1}/{len(self.data)}) Audio content written to file "{filename}.mp3"',
                    "INFO",
                )
                self.updateAnkiAudio.emit(x)
            except Exception as e:
                Logger().insert(e, "ERROR", False)
                Logger().insert(
                    "Something went wrong...Trying to Get Audio from Google...", "ERROR"
                )
                success = self.google_audio(x.chinese, filename)
                if success:
                    Logger().insert(
                        f'({i+1}/{len(self.data)}) Audio content written to file "{filename}.mp3"',
                        "INFO",
                    )
                    self.updateAnkiAudio.emit(x)
            sleep(randint(5, 15))
