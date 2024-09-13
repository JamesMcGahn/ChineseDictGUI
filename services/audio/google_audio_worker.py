from time import sleep

import google
from google.cloud import texttospeech
from PySide6.QtCore import QObject, Signal

from services import Logger
from utils import PathManager


class GoogleAudioWorker(QObject):
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
