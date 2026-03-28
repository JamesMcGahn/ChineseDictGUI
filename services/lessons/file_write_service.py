from models.dictionary import Lesson
from utils.files import PathManager


class LessonFileService:

    def write_dialogue(self, lesson: Lesson):
        PathManager.path_exists(lesson.storage_path, True)

        with open(
            f"{lesson.storage_path}dialogue.txt",
            "w",
            encoding="utf-8",
        ) as f:
            for sent in lesson.lesson_parts.dialogue:
                f.write(f"{sent.chinese}\n")

    def write_lesson_parts(self, lesson: Lesson):
        PathManager.path_exists(lesson.storage_path, True)

        with open(f"{lesson.storage_path}sentences.txt", "w", encoding="utf-8") as f:
            if lesson.lesson_parts.dialogue:
                f.write("对话:\n")
                for sent in lesson.lesson_parts.dialogue:
                    f.write(f"{sent.chinese}\n")

            if lesson.lesson_parts.expansion:
                f.write("例句:\n")
                for sent in lesson.lesson_parts.expansion:
                    f.write(f"{sent.chinese}\n")

            if lesson.lesson_parts.grammar:
                f.write("语法:\n")
                for grammar_point in lesson.lesson_parts.grammar:
                    f.write(f"{grammar_point.name}\n")
                    f.write(f"{grammar_point.explanation}\n")
                    for sent in grammar_point.examples:
                        f.write(f"{sent.chinese}\n")

            if lesson.lesson_parts.vocab:
                f.write("词汇:\n")
                for word in lesson.lesson_parts.vocab:
                    f.write(f"{word.chinese}\n")
