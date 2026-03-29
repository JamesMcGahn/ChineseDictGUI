import uuid
from collections import deque

from PySide6.QtCore import Signal

from base import QObjectBase
from base.enums import (
    LESSONPROVIDERS,
    PIPELINEJOBTYPE,
)
from models.pipelines import LessonPipelinePayload, PipelineRequest
from models.services import (
    LessonWorkFlowRequest,
)
from pipelines import BaseLessonPipeline, PipelineFactory
from services.network import TokenManager

from .audio_download_manager import AudioDownloadManager
from .database_service_manager import DatabaseServiceManager
from .ffmpeg_task_manager import FFmpegTaskManager
from .lingq_workflow_manager import LingqWorkFlowManager


# TODO move logic to pipeline
class LessonPipelineManager(QObjectBase):
    scraping_active = Signal(bool)
    ui_event = Signal(object)
    on_task_completed = Signal(object, object)

    def __init__(
        self,
        audio_download_manager: AudioDownloadManager,
        ffmpeg_task_manager: FFmpegTaskManager,
        lingq_workflow_manager: LingqWorkFlowManager,
        db: DatabaseServiceManager,
    ):
        super().__init__()
        self.ffmpeg_task_manager = ffmpeg_task_manager
        self.audio_download_manager = audio_download_manager
        self.lingq_workflow_manager = lingq_workflow_manager
        self.db = db
        self.token_manager = TokenManager()

        self.pipeline_queue: deque[PipelineRequest] = deque()
        self.current_pipeline: None | BaseLessonPipeline = None

    # TODO change name of method
    def enqueue_lessons(self, lesson_specs: list[LessonWorkFlowRequest]):

        for spec in lesson_specs:
            queue_id = str(uuid.uuid4())

            request = PipelineRequest(
                job_type=PIPELINEJOBTYPE.LESSONS,
                payload=LessonPipelinePayload(
                    queue_id=queue_id,
                    provider=LESSONPROVIDERS.CPOD,
                    url=spec.url,
                    check_dup_sents=spec.check_dup_sents,
                    transcribe_lesson=spec.transcribe_lesson,
                    create_lingq_lessons=True,
                ),
            )
            self.pipeline_queue.append(request)
        self.run_next()

    def on_pipeline_completed(self, queue_id):
        pipeline = self.current_pipeline
        self.logging(f"LessonPipelineManager - {queue_id} - completed")
        self.current_pipeline = None
        if pipeline:
            pipeline.ui_event.disconnect(self.ui_event)
            pipeline.pipeline_finished.disconnect(self.on_pipeline_completed)

        self.run_next()

    def run_next(self):
        if self.current_pipeline is not None:
            return

        if not self.pipeline_queue:
            return

        new_request = self.pipeline_queue.popleft()

        self.current_pipeline = PipelineFactory.get_pipeline(
            pipe_request=new_request,
            audio_download_manager=self.audio_download_manager,
            ffmpeg_task_manager=self.ffmpeg_task_manager,
            lingq_workflow_manager=self.lingq_workflow_manager,
            db=self.db,
        )

        self.current_pipeline.ui_event.connect(self.ui_event)
        self.current_pipeline.pipeline_finished.connect(self.on_pipeline_completed)

        self.current_pipeline.process()
