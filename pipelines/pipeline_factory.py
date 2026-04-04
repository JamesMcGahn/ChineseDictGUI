from base.enums import LESSONPROVIDERS, PIPELINEJOBTYPE
from models.pipelines import PipelineRequest, PipelineServiceContainer

from .base_pipeline import BaseLessonPipeline
from .cpod_lesson_pipeline import CPodLessonPipeline


class PipelineFactory:
    # TODO SERVICE CONTAINER?
    @staticmethod
    def get_pipeline(
        pipe_request: PipelineRequest, service_cont: PipelineServiceContainer
    ) -> BaseLessonPipeline:

        # TODO move to mapping
        if pipe_request.job_type == PIPELINEJOBTYPE.LESSONS:
            if pipe_request.payload.provider == LESSONPROVIDERS.CPOD:
                return CPodLessonPipeline(
                    spec=pipe_request.payload, service_cont=service_cont
                )

        else:
            raise ValueError("Unsupported source")
