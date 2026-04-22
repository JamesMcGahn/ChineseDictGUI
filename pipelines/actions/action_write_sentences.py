from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.sentences.models import Sentence

from dataclasses import dataclass, field

from .action_file_write_service import FileWriteAction


@dataclass
class WriteSentencesAction(FileWriteAction):
    header: str
    data: list[Sentence] = field(default_factory=list)
