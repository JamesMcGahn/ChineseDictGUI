from base.enums import UIEVENTTYPE
from models.core import LessonTaskPayload, UIEvent
from models.dictionary import Lesson
from models.pipelines import EmitUIEventAction, WriteSentencesAction
from models.services import ProcessorResponse

from ...base_section_processor import BaseSectionProcessor


class DialogueProcessor(BaseSectionProcessor):
    def __init__(self):
        super().__init__()

    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        self.logging("Processing Dialogue...")
        dialogue = payload.sentences
        lesson.lesson_parts.dialogue = dialogue
        lesson.lesson_parts.all_sentences.extend(dialogue)

        return ProcessorResponse(
            actions=[
                EmitUIEventAction(
                    event=UIEvent(
                        event_type=UIEVENTTYPE.SENTENCES,
                        data=dialogue,
                        check_duplicates=lesson.check_dup_sents,
                    )
                ),
                WriteSentencesAction(
                    write_path=lesson.storage_path,
                    file_name="dialogue.txt",
                    header="对话:",
                    data=dialogue,
                ),
            ]
        )
