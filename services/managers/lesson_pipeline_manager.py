from collections import deque

from PySide6.QtCore import Signal

from base import QObjectBase
from pipelines import BaseLessonPipeline, PipelineFactory
from pipelines.enums import PIPELINESTATUS
from pipelines.models import (
    PipelineRequest,
    PipelineResponse,
    PipelineServiceContainer,
)


# TODO move logic to pipeline
class LessonPipelineManager(QObjectBase):
    scraping_active = Signal(bool)
    ui_event = Signal(object)
    pipeline_response = Signal(object)

    def __init__(self, service_cont: PipelineServiceContainer):
        super().__init__()
        self.service_cont = service_cont

        self.pipeline_queue: deque[PipelineRequest] = deque()
        self.current_pipeline: None | BaseLessonPipeline = None

    def add_lessons_to_queue(self, requests: list[PipelineRequest]):
        self.pipeline_queue.extend(requests)
        self.run_next()

    def on_pipeline_completed(self, response: PipelineResponse):
        pipeline = self.current_pipeline

        print("RECEIVED in PIPELINE", response.status)
        if response.status in (
            PIPELINESTATUS.COMPLETE,
            PIPELINESTATUS.ERROR,
            PIPELINESTATUS.PARTIAL_ERROR,
        ):
            self.current_pipeline = None
            self.pipeline_response.emit(response)
            if pipeline:
                pipeline.ui_event.disconnect(self.ui_event)
                pipeline.pipeline_response.disconnect(self.on_pipeline_completed)

            self.run_next()
        else:
            self.pipeline_response.emit(response)

    def run_next(self):
        if self.current_pipeline is not None:
            return

        if not self.pipeline_queue:
            return

        new_request = self.pipeline_queue.popleft()

        self.current_pipeline = PipelineFactory.get_pipeline(
            pipe_request=new_request, service_cont=self.service_cont
        )

        self.current_pipeline.ui_event.connect(self.ui_event)
        self.current_pipeline.pipeline_response.connect(self.on_pipeline_completed)

        self.current_pipeline.process()
