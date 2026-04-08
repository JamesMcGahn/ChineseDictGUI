from typing import TYPE_CHECKING

from ..services.service_container import ServiceContainer

if TYPE_CHECKING:
    from services.managers import (
        AudioDownloadManager,
        FFmpegTaskManager,
        LingqWorkFlowManager,
    )
    from services.network.session import SessionRegistry

from dataclasses import dataclass


@dataclass()
class PipelineServiceContainer(ServiceContainer):
    audio: "AudioDownloadManager"
    ffmpeg: "FFmpegTaskManager"
    lingq: "LingqWorkFlowManager"
    session: "SessionRegistry"
