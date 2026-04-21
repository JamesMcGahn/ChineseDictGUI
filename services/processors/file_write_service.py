from pipelines.actions import (
    WriteGrammarAction,
    WriteLessonPartsAction,
    WriteSentencesAction,
    WriteWordsAction,
)

from ..base_file_write_service import BaseFileService


class LessonFileService(BaseFileService):

    def __init__(self):
        super().__init__()
        self.write_map[WriteLessonPartsAction] = self.write_lesson_parts

    def write_lesson_parts(self, action: WriteLessonPartsAction):
        if action.data.dialogue:
            self.write_sentences(
                action=WriteSentencesAction(
                    write_path=action.write_path,
                    file_name=action.file_name,
                    header="对话:",
                    data=action.data.dialogue,
                )
            )

        if action.data.expansion:
            self.write_sentences(
                action=WriteSentencesAction(
                    write_path=action.write_path,
                    file_name=action.file_name,
                    header="例句:",
                    data=action.data.expansion,
                )
            )

        if action.data.grammar:
            self.write_grammar(
                action=WriteGrammarAction(
                    write_path=action.write_path,
                    file_name=action.file_name,
                    header="语法:",
                    data=action.data.grammar,
                )
            )

        if action.data.vocab:
            self.write_words(
                action=WriteWordsAction(
                    write_path=action.write_path,
                    file_name=action.file_name,
                    header="词汇:",
                    data=action.data.vocab,
                )
            )
