from dataclasses import dataclass

from base.events import UIEvent

from .pipeline_action import PipelineAction


@dataclass
class EmitUIEventAction(PipelineAction):
    event: UIEvent
