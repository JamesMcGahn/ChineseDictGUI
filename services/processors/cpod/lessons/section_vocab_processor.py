from base.enums import UIEVENTTYPE
from base.events import UIEvent, WordsEvent
from models.core import LessonTaskPayload
from models.dictionary import Lesson
from models.pipelines import EmitUIEventAction, WriteWordsAction
from models.services import ProcessorResponse

from ...base_section_processor import BaseSectionProcessor


class VocabProcessor(BaseSectionProcessor):

    def __init__(self):
        super().__init__()

    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        self.logging("Processing Vocab...")
        words = payload.words
        lesson.lesson_parts.vocab = words

        return ProcessorResponse(
            actions=[
                EmitUIEventAction(
                    event=UIEvent(
                        event_type=UIEVENTTYPE.DISPLAY,
                        payload=WordsEvent(
                            words=words, check_duplicates=lesson.check_dup_words
                        ),
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
