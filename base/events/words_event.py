from dataclasses import dataclass, field

from models.dictionary import Word


@dataclass
class WordsEvent:
    words: list[Word] = field(default_factory=list)
    check_duplicates: bool = False
