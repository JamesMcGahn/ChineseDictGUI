from PySide6.QtCore import QThread, Signal, Slot

from base import QObjectBase
from core.scrapers.cpod.lessons import LessonScraperThread
from db import DatabaseManager, DatabaseQueryThread
from models.dictionary import Lesson, Sentence, Word
from services.network import TokenManager
from utils.files import PathManager


class LessonWorkFlowManager(QObjectBase):
    scraping_active = Signal(bool)
    send_sents_sig = Signal(list, bool)
    send_words_sig = Signal(list, bool)

    def __init__(self, audio_n_whisper_manager):
        super().__init__()
        self.audio_n_whisper_manager = audio_n_whisper_manager
        self.lesson_threads = []
        self.token_manager = TokenManager()

    def create_lesson_scrape(self, lessons):
        lesson_thread = LessonScraperThread(lessons)
        lesson_thread.request_token.connect(self.token_manager.request_token)
        self.token_manager.send_token.connect(lesson_thread.receive_token)
        lesson_thread.done.connect(lambda: self.remove_lesson_thread(lesson_thread))
        lesson_thread.lesson_done.connect(self.save_lesson)
        self.lesson_threads.append(lesson_thread)

        if len(self.lesson_threads) == 1:
            self.scraping_active.emit(True)
            lesson_thread.start()

    def remove_lesson_thread(self, thread):
        self.lesson_threads.remove(thread)
        try:
            thread.quit()
            thread.wait()
        except Exception:
            self.logging(f"Failed to quit Lesson Thread {thread}")
        thread.deleteLater()
        self.scraping_active.emit(False)

    def maybe_start_next_lesson(self):
        if self.lesson_threads:
            head = self.lesson_threads[0]
            if not head.isRunning() and not head.isFinished():
                self.scraping_active.emit(True)
                head.start()

    @Slot(str, str)
    def save_lesson(self, lesson: Lesson):
        all_sents = lesson.lesson_parts.all_sentences
        words = lesson.lesson_parts.vocab
        dialogue = lesson.lesson_parts.dialogue
        lesson_audios = lesson.lesson_parts.lesson_audios

        self.send_sents_sig.emit(all_sents, lesson.check_dup_sents)
        self.send_words_sig.emit(words, False)

        path = f"./test/{lesson.level}/{lesson.title}/"

        if not PathManager.path_exists(f"./test/{lesson.level}/{lesson.title}", True):
            print("path doesnt exist")
            return

        with open(f"{path}Dialogue.txt", "w", encoding="utf-8") as f:
            for sent in dialogue:
                f.write(f"{sent.chinese}\n")

        with open(f"{path}Sentences.txt", "w", encoding="utf-8") as f:
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

        sents_words_with_in_order = []
        for i, sent_item in enumerate(all_sents + words):
            sent_item.id = i + 1
            sents_words_with_in_order.append(sent_item)
            # return  # TODO REMOVE AFTER TESTING WHISPER
            # TODO add an option to disable downloading all sentences for lesson

        self.insert_lesson = DatabaseQueryThread(
            "lessons", "insert_lesson", lesson=lesson
        )
        self.insert_lesson.start()
        self.insert_lesson.finished.connect(self.insert_lesson.deleteLater)

        self.audio_n_whisper_manager.download_audio(
            lesson_audios,
            path,
            project_name=lesson.title,
        )

        if sents_words_with_in_order:
            self.logging(
                f"Adding - {lesson.title} - Sentences & Words Audio to Download Queue."
            )
            self.audio_n_whisper_manager.download_audio(
                sents_words_with_in_order,
                folder=f"{path}audio",
                update_db=False,
                combine_audio=True,
                combine_audio_export_folder=path,
                combine_audio_export_filename="Sentences.mp3",
                combine_audio_delay_between_audio=1500,
                project_name=lesson.title,
            )
