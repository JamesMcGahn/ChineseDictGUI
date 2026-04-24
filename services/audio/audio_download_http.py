import urllib.request

from models.services import (
    JobRequest,
)

from .base import BaseAudioDLProvider
from .models import AudioDownloadPayload
from .models.audio_download_validate import AudioDLValidationResult


class HTTPAudioDownload(BaseAudioDLProvider):

    def __init__(self, job: JobRequest[AudioDownloadPayload]):
        super().__init__(job=job)

    class Config:
        has_config = False
        provider_name = "Http"

    def validate_check(self):
        if not self.current_item.source_url:
            return AudioDLValidationResult(
                ok=False, fatal=False, message="Item does not have an audio link"
            )
        return AudioDLValidationResult(ok=True)

    def process_audio(self, path: str):
        checkHttp_url = self.current_item.source_url.replace("http://", "https://")
        urllib.request.urlretrieve(checkHttp_url, path)
