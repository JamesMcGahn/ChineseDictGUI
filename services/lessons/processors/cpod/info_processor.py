from base.enums import LESSONAUDIO
from models.core import LessonTaskPayload
from models.dictionary import Lesson, LessonAudio
from models.services import ProcessorResponse

from ..base_lesson_processor import BaseLessonProcessor


class CPodLessonInfoProcessor(BaseLessonProcessor):
    def __init__(self):
        # TODO set app data base path
        self.base_path = "./test/"

    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        lesson_info = payload.lesson_info

        lesson.hash_code = lesson_info.hash_code
        lesson.level = lesson_info.level
        lesson.lesson_id = lesson_info.lesson_id
        lesson.title = lesson_info.title
        lesson.slug = lesson_info.slug

        path = f"{self.base_path}{lesson.level}/{lesson.title}/"
        lesson.storage_path = path

        dialogue_audio = LessonAudio(
            title="dialogue",
            audio_type=LESSONAUDIO.DIALOGUE,
            audio=lesson_info.dialogue_audio,
            level=lesson.level,
            lesson=lesson.title,
            transcribe=False,
        )

        lesson_audio = LessonAudio(
            title="lesson",
            audio_type=LESSONAUDIO.LESSON,
            audio=lesson_info.lesson_audio,
            level=lesson.level,
            lesson=lesson.title,
            transcribe=lesson.transcribe_lesson,
        )
        lesson.lesson_parts.lesson_audios.append(dialogue_audio)
        lesson.lesson_parts.lesson_audios.append(lesson_audio)

        return ProcessorResponse()
