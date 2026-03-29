from dataclasses import dataclass, field

from base.enums import UIEVENTTYPE

from ..dictionary import Sentence, Word


@dataclass
class UIEvent:
    type: UIEVENTTYPE
    data: list[Sentence] | list[Word] = field(default_factory=list)
    check_duplicates: bool = False
