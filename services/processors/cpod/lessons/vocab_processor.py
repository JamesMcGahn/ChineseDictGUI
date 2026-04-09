from base.enums import UIEVENTTYPE
from models.core import LessonTaskPayload, UIEvent
from models.dictionary import Lesson
from models.pipelines import EmitUIEventAction, WriteWordsAction
from models.services import ProcessorResponse

from ...base_lesson_processor import BaseLessonProcessor


class CPodLessonVocabProcessor(BaseLessonProcessor):
    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        words = payload.words
        lesson.lesson_parts.vocab = words

        return ProcessorResponse(
            actions=[
                EmitUIEventAction(
                    event=UIEvent(
                        event_type=UIEVENTTYPE.WORDS,
                        data=words,
                        check_duplicates=lesson.check_dup_sents,
                    )
                ),
                WriteWordsAction(
                    write_path=lesson.storage_path,
                    file_name="vocab.txt",
                    header="词汇:",
                    data=words,
                ),
            ]
        )
