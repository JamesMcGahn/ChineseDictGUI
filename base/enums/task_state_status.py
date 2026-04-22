from enum import StrEnum


class TASKSTATESTATUS(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"
    SKIPPED = "skipped"
