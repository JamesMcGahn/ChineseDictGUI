from typing import TYPE_CHECKING

from .service_container import ServiceContainer

if TYPE_CHECKING:
    from services.managers import (
        AudioDownloadManager,
        FFmpegTaskManager,
        LingqWorkFlowManager,
    )
    from services.network import SessionRegistry

from dataclasses import dataclass


@dataclass()
class ContextServiceContainer(ServiceContainer):
    audio: "AudioDownloadManager"
    ffmpeg: "FFmpegTaskManager"
    lingq: "LingqWorkFlowManager"
    session: "SessionRegistry"
