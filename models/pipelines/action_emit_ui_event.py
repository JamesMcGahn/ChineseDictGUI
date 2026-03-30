from dataclasses import dataclass

from ..core import UIEvent
from .pipeline_action import PipelineAction


@dataclass
class EmitUIEventAction(PipelineAction):
    event: UIEvent
