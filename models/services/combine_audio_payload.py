from dataclasses import dataclass, field


@dataclass(frozen=True)
class CombineAudioPayload:
    combine_folder_path: str
    export_file_name: str = field(default="combine_audio.mp3")
    export_path: str = field(default="./")
    delay_between_audio: int = field(default=1500)
    project_name: str = field(default=None)
