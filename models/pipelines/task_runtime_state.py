from dataclasses import dataclass


@dataclass
class TaskRuntimeState:
    retry_attempts: int = 0
    source_index: int = 0
