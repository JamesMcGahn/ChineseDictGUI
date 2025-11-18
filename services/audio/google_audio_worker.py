import google
from google.cloud import texttospeech
from PySide6.QtCore import QTimer, Signal, Slot

from base import QObjectBase
from utils.files import PathManager


class GoogleAudioWorker(QObjectBase):
    success = Signal(object)
    error = Signal()
    finished = Signal()

    def __init__(
        self,
        text,
        filename,
        folder_path="./",
        access_key_location="./key.json",
        success_message="Google Audio Successfully Downloaded.",
        audio_object=None,
        project_name="",
    ):
        super().__init__()
        self.text = text
        self.google_tried = False
        self.filename = filename
        self.folder_path = folder_path
        self.access_key_location = access_key_location
        self.audio_object = audio_object
        self.success_message = success_message
        self.project_name = project_name

    @Slot()
    def do_work(self):
        self.logging(f"Starting Google Audio Worker in thread {self.thread()}")
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

            path = PathManager.check_dup(self.folder_path, self.filename, ".mp3")

            with open(path, "wb") as out:
                out.write(response.audio_content)
            self.logging(self.success_message)
            self.success.emit(self.audio_object)
            self.send_finished()
        except google.api_core.exceptions.ServiceUnavailable as e:
            self.maybe_try_again(e)
        except Exception as e:
            self.maybe_try_again(e)

    def send_finished(self):
        self.finished.emit()

    def maybe_try_again(self, e):
        if self.google_tried is False:
            failure_msg_retry = f"({self.project_name} - {self.filename}.mp3) - Failed to get Audio From Google...Trying Again..."
            self.logging(failure_msg_retry, "WARN")
            self.google_tried = True
            backoff_time = 1000 * 15
            QTimer.singleShot(backoff_time, self.do_work)
        else:
            self.logging(
                f"({self.project_name} - {self.filename}.mp3)Failed to get Audio From Google",
                "ERROR",
            )
            self.logging(e, "ERROR", False)
            self.send_finished()
            return False
