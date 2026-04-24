from dataclasses import dataclass


@dataclass
class AudioDLValidationResult:
    ok: bool
    fatal: bool = False
    message: str = ""
