from dataclasses import dataclass, field


@dataclass(frozen=True)
class FasterWhisperOptions:
    compute_type: str = field(default="auto")
    beam_size: int = field(default=8)
    min_silence_ms: int = field(default=2500)
    chunk_length: int = field(default=120)
    vad_filter: bool = field(default=False)
    multilingual: bool = field(default=False)
    on_previous_text: bool = field(default=True)
