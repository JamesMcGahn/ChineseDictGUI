from dataclasses import dataclass


@dataclass(frozen=True)
class TaskCapability:
    transform: bool = False
    process: bool = False
