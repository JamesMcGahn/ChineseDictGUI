from typing import TYPE_CHECKING

from base.enums import LESSONPROVIDERS, PIPELINEJOBTYPE
from models.pipelines import PipelineRequest

from .base_pipeline import BaseLessonPipeline
from .cpod_lesson_pipeline import CPodLessonPipeline

if TYPE_CHECKING:
    from services.managers import (
        AudioDownloadManager,
        DatabaseServiceManager,
        FFmpegTaskManager,
        LingqWorkFlowManager,
    )


class PipelineFactory:
    # TODO SERVICE CONTAINER?
    @staticmethod
    def get_pipeline(
        pipe_request: PipelineRequest,
        audio_download_manager: "AudioDownloadManager",
        ffmpeg_task_manager: "FFmpegTaskManager",
        lingq_workflow_manager: "LingqWorkFlowManager",
        db: "DatabaseServiceManager",
    ) -> BaseLessonPipeline:

        # TODO move to mapping
        if pipe_request.job_type == PIPELINEJOBTYPE.LESSONS:
            if pipe_request.payload.provider == LESSONPROVIDERS.CPOD:
                return CPodLessonPipeline(
                    spec=pipe_request.payload,
                    audio_download_manager=audio_download_manager,
                    ffmpeg_task_manager=ffmpeg_task_manager,
                    lingq_workflow_manager=lingq_workflow_manager,
                    db=db,
                )

        else:
            raise ValueError("Unsupported source")
