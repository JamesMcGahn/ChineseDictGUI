from dataclasses import dataclass, field


@dataclass(frozen=True)
class LingqLessonPayload:
    title: str
    collection: str
    audio_file_name: str
    audio_file_path: str
    text_file_name: str
    text_file_path: str
    project_name: str = field(default=None)
    language: str = field(default="zh")
