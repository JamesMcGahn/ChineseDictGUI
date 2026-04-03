from dataclasses import dataclass


@dataclass(frozen=True)
class WhisperResponse:
    filename: str
    path: str
    full_path: str
