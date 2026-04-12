from dataclasses import dataclass, field

from base.enums import LESSONTASK

from .task_capabilities import TaskCapability
from .task_policy import TaskPolicy


@dataclass
class TaskDefinition:
    next_tasks: list[LESSONTASK] = field(default_factory=list)
    sources: list = field(default_factory=list)
    policy: TaskPolicy = field(default_factory=TaskPolicy)
    capability: TaskCapability = field(default_factory=TaskCapability)
