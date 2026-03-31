from pathlib import Path

from base import QObjectBase
from models.pipelines import (
    FileWriteAction,
    WriteGrammarAction,
    WriteLessonPartsAction,
    WriteSentencesAction,
    WriteWordsAction,
)
from utils.files import PathManager


class LessonFileService(QObjectBase):

    def __init__(self):
        self.write_map = {
            WriteWordsAction: self.write_words,
            WriteSentencesAction: self.write_sentences,
            WriteGrammarAction: self.write_grammar,
            WriteLessonPartsAction: self.write_lesson_parts,
        }

    def write_file(self, action: FileWriteAction):
        handler = self.write_map.get(type(action), None)
        if not handler:
            self.logging(
                f"{self.__class__.__name__}: {type(action)} has not been implemented",
                "ERROR",
            )
            raise NotImplementedError()
        handler(action)

    def _append_lines(self, file_path, header, lines):
        with open(file_path, "a", encoding="utf-8") as f:
            if header:
                f.write(f"{header}\n")
            for line in lines:
                f.write(f"{line}\n")

    def write_words(self, action: WriteWordsAction):
        PathManager.path_exists(action.write_path, True)
        path = Path(action.write_path) / action.file_name
        lines = [word.chinese for word in action.data]
        self._append_lines(file_path=path, header=action.header, lines=lines)

    def write_sentences(self, action: WriteSentencesAction):
        PathManager.path_exists(action.write_path, True)
        path = Path(action.write_path) / action.file_name
        lines = [sentence.chinese for sentence in action.data]
        self._append_lines(file_path=path, header=action.header, lines=lines)

    def write_grammar(self, action: WriteGrammarAction):
        PathManager.path_exists(action.write_path, True)
        path = Path(action.write_path) / action.file_name

        lines = []
        for grammar_point in action.data:
            lines.append(f"{grammar_point.name}")
            lines.append(f"{grammar_point.explanation}")
            for sent in grammar_point.examples:
                lines.append(f"{sent.chinese}")
            lines.append("")
        self._append_lines(file_path=path, header=action.header, lines=lines)

    def write_lesson_parts(self, action: WriteLessonPartsAction):
        PathManager.path_exists(action.write_path, True)

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
