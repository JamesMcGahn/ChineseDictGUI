from base.enums import UIEVENTTYPE
from models.core import LessonTaskPayload, UIEvent
from models.dictionary import Lesson
from models.pipelines import EmitUIEventAction
from models.services import ProcessorResponse

from ...base_section_processor import BaseSectionProcessor


class ExpansionProcessor(BaseSectionProcessor):
    def __init__(self):
        super().__init__()

    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        self.logging("Processing Expansion...")
        expansion = payload.sentences
        lesson.lesson_parts.expansion = expansion
        lesson.lesson_parts.all_sentences.extend(expansion)

        return ProcessorResponse(
            actions=[
                EmitUIEventAction(
                    event=UIEvent(
                        event_type=UIEVENTTYPE.SENTENCES,
                        data=expansion,
                        check_duplicates=lesson.check_dup_sents,
                    )
                )
            ]
        )
