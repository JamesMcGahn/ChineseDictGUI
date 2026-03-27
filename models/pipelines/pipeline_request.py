from dataclasses import dataclass, field

from base.enums import PIPELINEJOBTYPE

from .lesson_pipeline_payload import LessonPipelinePayload


@dataclass(frozen=True)
class PipelineRequest:
    job_type: PIPELINEJOBTYPE
    payload: LessonPipelinePayload
