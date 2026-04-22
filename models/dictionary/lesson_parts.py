from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.words.models import Word
    from services.sentences.models import Sentence

from dataclasses import dataclass, field

from .grammar_point import GrammarPoint
from .lesson_audio import LessonAudio


@dataclass
class LessonParts:
    lesson_audios: list[LessonAudio] = field(default_factory=list)
    dialogue: list[Sentence] = field(default_factory=list)
    expansion: list[Sentence] = field(default_factory=list)
    grammar: list[GrammarPoint] = field(default_factory=list)
    vocab: list[Word] = field(default_factory=list)
    all_sentences: list[Sentence] = field(default_factory=list)
