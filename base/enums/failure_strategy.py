from enum import Enum


class FAILURESTRATEGY(Enum):
    RETRY = "retry"
    FAIL = "fail"
    FALLBACK = "fallback"
    IGNORE = "ignore"
