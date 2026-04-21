from dataclasses import dataclass

from base.enums import TASKSTATESTATUS


@dataclass
class TaskRuntimeState:
    status: TASKSTATESTATUS = TASKSTATESTATUS.PENDING
    retry_attempts: int = 0
    source_index: int = 0
    downstream_dispatched: bool = False
