from dataclasses import dataclass, field

from base.enums import EXTRACTDATASOURCE
from models.dictionary import GrammarPoint, Sentence, Word

from .lesson_info import LessonInfo


@dataclass
class LessonTaskPayload:
    success: bool
    data_source: EXTRACTDATASOURCE
    lesson_info: LessonInfo | None = None
    sentences: list[Sentence] = field(default_factory=list)
    words: list[Word] = field(default_factory=list)
    grammar: list[GrammarPoint] = field(default_factory=list)
