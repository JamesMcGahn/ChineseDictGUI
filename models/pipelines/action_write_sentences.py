from dataclasses import dataclass, field

from models.dictionary import Sentence

from .action_file_write_service import FileWriteAction


@dataclass
class WriteSentencesAction(FileWriteAction):
    header: str
    data: list[Sentence] = field(default_factory=list)
