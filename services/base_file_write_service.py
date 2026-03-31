from pathlib import Path

from base import QObjectBase
from models.pipelines import (
    FileWriteAction,
    WriteGrammarAction,
    WriteSentencesAction,
    WriteWordsAction,
)
from utils.files import PathManager


class BaseFileService(QObjectBase):

    def __init__(self):
        self.write_map = {
            WriteWordsAction: self.write_words,
            WriteSentencesAction: self.write_sentences,
            WriteGrammarAction: self.write_grammar,
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
