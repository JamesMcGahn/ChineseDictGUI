from dataclasses import dataclass


@dataclass(frozen=True)
class CombineAudioResponse:
    filename: str
    path: str
    full_path: str
