from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.words.models import Word

from dataclasses import dataclass, field


@dataclass
class WordsEvent:
    words: list[Word] = field(default_factory=list)
    check_duplicates: bool = False
