from dataclasses import dataclass

from base.enums import LESSONAUDIO


@dataclass
class LessonAudio:
    title: str
    audio_type: LESSONAUDIO
    audio: str
    level: str | None = None
    id: int = 0
    lesson: str | None = ""
    transcribe: bool = True
