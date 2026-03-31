from dataclasses import dataclass, field

from models.dictionary import GrammarPoint

from .action_file_write_service import FileWriteAction


@dataclass
class WriteGrammarAction(FileWriteAction):
    header: str
    data: list[GrammarPoint] = field(default_factory=list)
