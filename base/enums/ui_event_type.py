from enum import StrEnum


class UIEVENTTYPE(StrEnum):
    DISPLAY = "display"
    UPDATE = "update"
    ERROR = "error"
    LOADING = "loading"
