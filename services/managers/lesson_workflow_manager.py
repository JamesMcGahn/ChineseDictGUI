import uuid

from PySide6.QtCore import QThread, Signal, Slot

from base import QObjectBase
from base.enums import JOBSTATUS, LESSONAUDIO, LESSONTASK
from core.scrapers.cpod.lessons import LessonScraperThread
from db import DatabaseManager, DatabaseQueryThread
from models.dictionary import Lesson, LessonAudio, Sentence, Word
from models.services import AudioDownloadPayload, JobRef
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
        self.lessons_queue = {}

        self.base_path = "./test/"

    def create_lesson_scrape(self, lesson_specs):
        jobs = []
        for spec in lesson_specs:
            queue_id = uuid.uuid4()

            add_lesson = Lesson(
                provider=spec["provider"],
                url=spec["url"],
                check_dup_sents=spec["check_dup_sents"],
                transcribe_lesson=spec["transcribe_lesson"],
                queue_id=queue_id,
                slug="",
            )

            new_spec = {
                "provider": "cpod",
                "slug": "",
                "queue_id": queue_id,
                "url": spec["url"],
                "check_dup_sents": spec["check_dup_sents"],
                "transcribe_lesson": spec["transcribe_lesson"],
            }

            self.lessons_queue[queue_id] = add_lesson
            jobs.append(new_spec)

        lesson_thread = LessonScraperThread(jobs)
        lesson_thread.request_token.connect(self.token_manager.request_token)
        lesson_thread.task_complete.connect(self.on_task_completed)
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

        if sents_words_with_in_order:
            self.logging(
                f"Adding - {lesson.title} - Sentences & Words Audio to Download Queue."
            )
            # TODO move parmeters to payload
            self.audio_n_whisper_manager.download_audio(
                JobRef(
                    id=lesson.queue_id, task=LESSONTASK.AUDIO, status=JOBSTATUS.CREATED
                ),
                AudioDownloadPayload(
                    audio_urls=sents_words_with_in_order,
                    export_path=f"{lesson.storage_path}audio",
                    project_name=lesson.title,
                ),
            )

            # combine_audio=False,
            # combine_audio_export_folder=path,
            # combine_audio_export_filename="Sentences.mp3",
            # combine_audio_delay_between_audio=1500,

    def on_task_completed(self, job: JobRef, payload):
        print("here", job)
        if job.id not in self.lessons_queue:
            return

        lesson: Lesson = self.lessons_queue[job.id]

        if lesson is None:
            return

        if job.task == LESSONTASK.LESSON_AUDIO and job.status == JOBSTATUS.COMPLETE:
            if lesson.transcribe_lesson:
                self.audio_n_whisper_manager.whisper_audio(
                    lesson.storage_path, LESSONAUDIO.LESSON
                )

        if job.task == LESSONTASK.AUDIO and job.status == JOBSTATUS.COMPLETE:
            self.audio_n_whisper_manager.combine_audio(
                f"{lesson.storage_path}audio",
                "sentences.mp3",
                lesson.storage_path,
                1500,
                lesson.title,
            )

        if job.task == LESSONTASK.INFO and job.status == JOBSTATUS.COMPLETE:
            lesson.hash_code = payload["hash_code"]
            lesson.level = payload["level"]
            lesson.lesson_id = payload["lesson_id"]
            lesson.title = payload["title"]
            lesson.slug = payload["slug"]

            path = f"{self.base_path}{lesson.level}/{lesson.title}/"
            lesson.storage_path = path

            dialogue_audio = LessonAudio(
                title="dialogue",
                audio_type=LESSONAUDIO.DIALOGUE,
                audio=payload["dialogue_audio"],
                level=lesson.level,
                lesson=lesson.title,
                transcribe=False,
            )

            lesson_audio = LessonAudio(
                title="lesson",
                audio_type=LESSONAUDIO.LESSON,
                audio=payload["lesson_audio"],
                level=lesson.level,
                lesson=lesson.title,
                transcribe=lesson.transcribe_lesson,
            )
            lesson.lesson_parts.lesson_audios.append(dialogue_audio)
            lesson.lesson_parts.lesson_audios.append(lesson_audio)

            self.audio_n_whisper_manager.download_audio(
                jobref=JobRef(
                    lesson.queue_id, LESSONTASK.LESSON_AUDIO, JOBSTATUS.CREATED
                ),
                payload=AudioDownloadPayload(
                    audio_urls=lesson.lesson_parts.lesson_audios,
                    export_path=lesson.storage_path,
                    project_name=lesson.title,
                ),
            )

        if job.task == LESSONTASK.LESSON_AUDIO and job.status == JOBSTATUS.COMPLETE:
            print("Todo for whisper")
            # TODO WHISPER

        if job.task == LESSONTASK.DIALOGUE and job.status == JOBSTATUS.COMPLETE:
            dialogue = payload["sentences"]
            lesson.lesson_parts.dialogue = dialogue
            lesson.lesson_parts.all_sentences.extend(dialogue)
            PathManager.path_exists(lesson.storage_path, True)
            self.send_sents_sig.emit(dialogue, lesson.check_dup_sents)
            with open(
                f"{lesson.storage_path}dialogue.txt",
                "w",
                encoding="utf-8",
            ) as f:
                for sent in dialogue:
                    f.write(f"{sent.chinese}\n")

        if job.task == LESSONTASK.VOCAB and job.status == JOBSTATUS.COMPLETE:
            words = payload["words"]
            lesson.lesson_parts.vocab = words
            self.send_words_sig.emit(words, False)

        if job.task == LESSONTASK.EXPANSION and job.status == JOBSTATUS.COMPLETE:
            expansion = payload["sentences"]
            lesson.lesson_parts.expansion = expansion
            lesson.lesson_parts.all_sentences.extend(expansion)
            self.send_sents_sig.emit(expansion, lesson.check_dup_sents)

        if job.task == LESSONTASK.GRAMMAR and job.status == JOBSTATUS.COMPLETE:
            grammar_points = payload["grammar"]
            sentences = payload["sentences"]
            lesson.lesson_parts.grammar = grammar_points
            lesson.lesson_parts.all_sentences.extend(sentences)
            self.send_sents_sig.emit(sentences, lesson.check_dup_sents)

        if job.task == LESSONTASK.CHECK and job.status == JOBSTATUS.COMPLETE:
            self.save_lesson(lesson)
