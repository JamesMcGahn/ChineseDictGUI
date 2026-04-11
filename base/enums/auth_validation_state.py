from enum import StrEnum


class AUTHVALIDATIONSTATUS(StrEnum):
    VALID = "valid"
    STARTED = "started"
    BUSY = "busy"
    FAILED = "failed"
    COOLDOWN = "cool_down"
    UNSUPPORTED = "unsupported"
