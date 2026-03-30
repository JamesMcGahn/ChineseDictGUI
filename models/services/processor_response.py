from dataclasses import dataclass, field

from ..pipelines import PipelineAction


@dataclass
class ProcessorResponse:
    actions: list[PipelineAction] = field(default_factory=list)
