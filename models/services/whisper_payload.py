from dataclasses import dataclass, field

from base.enums import WHISPERPROVIDER

from .faster_whisper_options import FasterWhisperOptions


@dataclass(frozen=True)
class WhisperPayload:
    provider: WHISPERPROVIDER
    file_folder_path: str
    file_filename: str
    model_name: str = field(default="medium")
    initial_prompt: str = field(
        default="Transcribe Mandarin using Simplified Chinese characters. "
    )
    language: str = field(default="zh")
    options: FasterWhisperOptions | None = field(default=None)
