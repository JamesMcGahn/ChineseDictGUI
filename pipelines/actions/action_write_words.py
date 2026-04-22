from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.words.models import Word

from dataclasses import dataclass, field

from .action_file_write_service import FileWriteAction


@dataclass
class WriteWordsAction(FileWriteAction):
    header: str
    data: list[Word] = field(default_factory=list)
