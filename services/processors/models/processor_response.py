from dataclasses import dataclass, field

from pipelines.actions import PipelineAction


@dataclass
class ProcessorResponse:
    actions: list[PipelineAction] = field(default_factory=list)
