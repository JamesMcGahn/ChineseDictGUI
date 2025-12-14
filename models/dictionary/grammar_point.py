from dataclasses import dataclass, field

from .sentence import Sentence


@dataclass
class GrammarPoint:
    name: str
    explanation: str | None
    examples: list[Sentence] = field(default_factory=list)
