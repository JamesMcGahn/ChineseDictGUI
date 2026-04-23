from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....lessons.models import LessonTaskPayload

from models.dictionary import Lesson
from services.audio.models import AudioItem

from ...base_section_processor import BaseSectionProcessor
from ...models import ProcessorResponse


class InfoProcessor(BaseSectionProcessor):
    def __init__(self):
        super().__init__()
        # TODO set app data base path
        self.base_path = "./test/"

    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        self.logging("Processing Lesson info...")
        lesson_info = payload.lesson_info

        lesson.hash_code = lesson_info.hash_code
        lesson.level = lesson_info.level
        lesson.lesson_id = lesson_info.lesson_id
        lesson.title = lesson_info.title
        lesson.slug = lesson.slug or lesson_info.slug

        path = f"{self.base_path}{lesson.level}/{lesson.title}/"
        lesson.storage_path = path

        dialogue_audio = AudioItem(
            lesson.queue_id,
            file_name="dialogue",
            target_path=path,
            source_url=lesson_info.dialogue_audio,
            text=None,
        )

        lesson_audio = AudioItem(
            lesson.queue_id,
            file_name="lesson",
            target_path=path,
            source_url=lesson_info.lesson_audio,
            text=None,
        )

        lesson.lesson_parts.lesson_audios.extend([dialogue_audio, lesson_audio])

        return ProcessorResponse()
