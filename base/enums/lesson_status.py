from enum import StrEnum


class LESSONSTATUS(StrEnum):
    CREATED = "created"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    ERROR = "error"
