from dataclasses import dataclass, field

from models.dictionary import Sentence


@dataclass
class SentencesEvent:
    sentences: list[Sentence] = field(default_factory=list)
    check_duplicates: bool = False
