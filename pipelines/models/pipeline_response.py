from dataclasses import dataclass
from typing import Generic, TypeVar

from pipelines.enums import PIPELINEJOBTYPE

from ..enums import PIPELINESTATUS

P = TypeVar("P")


@dataclass(frozen=True)
class PipelineResponse(Generic[P]):
    job_type: PIPELINEJOBTYPE
    status: PIPELINESTATUS
    payload: P
