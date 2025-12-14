from dataclasses import dataclass, field

from .grammar_point import GrammarPoint
from .lesson_audio import LessonAudio
from .sentence import Sentence


@dataclass
class LessonParts:
    lesson_audios: list[LessonAudio] = field(default_factory=list)
    dialogue: list[Sentence] = field(default_factory=list)
    expansion: list[Sentence] = field(default_factory=list)
    grammar: list[GrammarPoint] = field(default_factory=list)
    all_sentences: list[Sentence] = field(default_factory=list)
