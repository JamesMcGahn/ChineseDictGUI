from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.sentences.models import Sentence

from dataclasses import dataclass, field


@dataclass
class GrammarPoint:
    name: str
    explanation: str | None
    examples: list[Sentence] = field(default_factory=list)
