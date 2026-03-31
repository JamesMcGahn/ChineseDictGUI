from dataclasses import dataclass, field

from models.dictionary import Word

from .action_file_write_service import FileWriteAction


@dataclass
class WriteWordsAction(FileWriteAction):
    header: str
    data: list[Word] = field(default_factory=list)
