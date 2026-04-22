from enum import StrEnum


class PIPELINESTATUS(StrEnum):
    CREATED = "created"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    PARTIAL_ERROR = "partial_error"
    ERROR = "error"
