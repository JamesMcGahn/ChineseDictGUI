from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.words.models import Word

from dataclasses import dataclass, field

from base.enums import EXTRACTDATASOURCE
from models.dictionary import GrammarPoint, Sentence

from .lesson_info import LessonInfo


@dataclass
class LessonTaskPayload:
    success: bool
    data_source: EXTRACTDATASOURCE
    lesson_info: LessonInfo | None = None
    sentences: list[Sentence] = field(default_factory=list)
    words: list[Word] = field(default_factory=list)
    grammar: list[GrammarPoint] = field(default_factory=list)
