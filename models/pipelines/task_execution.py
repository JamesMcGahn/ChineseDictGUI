from dataclasses import dataclass

from .task_capabilities import TaskCapability
from .task_policy import TaskPolicy
from .task_runtime_state import TaskRuntimeState


@dataclass
class TaskExecution:
    policy: TaskPolicy
    capability: TaskCapability | None
    state: TaskRuntimeState
