from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.sentences.models import Sentence

from dataclasses import dataclass, field


@dataclass
class SentencesEvent:
    sentences: list[Sentence] = field(default_factory=list)
    check_duplicates: bool = False
