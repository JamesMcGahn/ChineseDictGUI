import json

from google.api_core.exceptions import ServiceUnavailable
from google.cloud.texttospeech import (
    AudioConfig,
    AudioEncoding,
    SsmlVoiceGender,
    TextToSpeechClient,
    VoiceSelectionParams,
)

from models.services import (
    JobRequest,
)

from .base import BaseAudioDLProvider, RetryableAudioError
from .models import AudioDownloadPayload
from .models.audio_download_validate import AudioDLValidationResult


class GoogleAudioDownload(BaseAudioDLProvider):
    def __init__(
        self,
        job: JobRequest[AudioDownloadPayload],
        google_audio_credential="",
    ):
        super().__init__(job=job)
        # TODO remove get from setting
        self.access_key_location = "./key.json"
        self.google_audio_credential = google_audio_credential

        self.google_client: TextToSpeechClient | None = None
        self.google_voice: VoiceSelectionParams | None = None
        self.google_audio_config = AudioConfig(audio_encoding=AudioEncoding.MP3)

    class Config:
        has_config = True
        provider_name = "Google"

    def setup_config(self):
        self.setup_client()
        self.set_up_voice()

    def validate_check(self):
        if not self.current_item.text:
            return AudioDLValidationResult(
                ok=False, fatal=False, message="Item does not have any text."
            )

        if not self.google_client or not self.google_voice:
            return AudioDLValidationResult(
                ok=False, fatal=True, message="Google Client is not set up"
            )
        return AudioDLValidationResult(ok=True)

    def process_audio(self, path: str):
        try:
            response = self.google_client.synthesize_speech(
                request={
                    "input": self.current_item.text,
                    "voice": self.google_voice,
                    "audio_config": self.google_audio_config,
                }
            )

            with open(path, "wb") as out:
                out.write(response.audio_content)
        except ServiceUnavailable as e:
            raise RetryableAudioError(e, 90) from e

    def setup_client(self):
        try:
            if self.google_audio_credential:

                service_account_info = json.loads(self.google_audio_credential)

            elif self.access_key_location:
                with open(self.access_key_location, "r", encoding="utf-8") as f:
                    service_account_info = json.load(f)
            else:
                raise ValueError("Service account json file or string not provided.")

            self.google_client = TextToSpeechClient.from_service_account_info(
                service_account_info
            )
        except Exception as e:
            self.complete_failure("Failed to initiate google client.")
            self.logging(str(e), "DEBUG")

    def set_up_voice(self):
        # FEATURE change voice?
        self.google_voice = VoiceSelectionParams(
            language_code="cmn-CN", ssml_gender=SsmlVoiceGender.FEMALE
        )
