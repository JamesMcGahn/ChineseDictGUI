from dataclasses import dataclass


@dataclass
class LessonAudio:
    title: str
    audio_type: str
    audio: str
    level: str | None = None
    id: int = 0
    lesson: str | None = ""
    transcribe: bool = True
