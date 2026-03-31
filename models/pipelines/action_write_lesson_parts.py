from dataclasses import dataclass

from models.dictionary import LessonParts

from .action_file_write_service import FileWriteAction


@dataclass
class WriteLessonPartsAction(FileWriteAction):
    header: str
    data: LessonParts
