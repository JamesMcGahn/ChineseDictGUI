import re
import uuid
from collections import deque
from random import randint
from urllib.parse import urlparse

from PySide6.QtCore import QMutexLocker, QThread, QTimer, Signal, Slot

from base import QWorkerBase, ThreadCleanUpManager
from base.enums import (
    JOBSTATUS,
    LESSONAUDIO,
    LESSONLEVEL,
    LESSONSTATUS,
    LESSONTASK,
    LOGLEVEL,
)
from keys import keys
from models.dictionary import GrammarPoint, Lesson, LessonAudio, Sentence, Word
from models.services import JobRef, NetworkResponse
from services.network import NetworkWorker


class LessonScraperWorkerV2(QWorkerBase):
    finished = Signal()
    send_sents_sig = Signal(list)
    send_words_sig = Signal(list)
    send_dialogue = Signal(object, object)
    lesson_done = Signal(object)
    request_token = Signal()
    lesson_status = Signal(object)
    task_complete = Signal(object, object)

    def __init__(self, lesson_list, mutex, wait_condition, parent_thread):
        super().__init__()
        self.lesson_list = deque(lesson_list)
        self._mutex = mutex
        self._wait_condition = wait_condition
        self.parent_thread = parent_thread
        self.temp_file_paths = []
        self.host_url = keys["url"]
        self.audio_host_url = keys["audio_host"]
        self.token = None
        self.wait_time_between_reqs = (5, 15)

        self.current_lesson: Lesson | None = None
        self.completed_lessons = []
        self.errored_lessons = []
        self.running_tasks = {}
        self.clean_up_manager = ThreadCleanUpManager()
        self.current_lesson_checked = False

    @Slot()
    def do_work(self):
        self.log_thread()
        if self.token:
            self.get_next_lesson()
        else:
            self.request_token.emit()

    @Slot()
    def receive_token(self, token):
        self.token = token
        self.get_next_lesson()

    def wait_time(self, range, fn):
        random = randint(*range)
        self.logging(
            f"LessonWorker: Waiting {random} secs before sending out next request."
        )
        QTimer.singleShot(random * 1000, fn)

    def send_status_update(self, status: LESSONSTATUS, task: LESSONTASK):
        self.lesson_status.emit(
            {
                "queue_id": self.current_lesson.queue_id,
                "status": status,
                "task": task,
            }
        )

    def get_next_lesson(self):
        self.current_lesson = None
        self.current_lesson_checked = False
        self.logging(f"Total Lessons to Scrape: {len(self.lesson_list)} Lessons")
        if not self.token:
            self.request_token.emit()
            return

        if self.lesson_list:
            with QMutexLocker(self._mutex):
                if self.parent_thread._stop:
                    self.finished.emit()

                while self.parent_thread._paused:
                    self._wait_condition.wait(self._mutex)

            spec = self.lesson_list.popleft()
            self.current_lesson = Lesson(
                provider=spec["provider"],
                url=spec["url"],
                check_dup_sents=spec["check_dup_sents"],
                transcribe_lesson=spec["transcribe_lesson"],
                queue_id=spec["queue_id"],
                slug="",
            )

            self.send_status_update(LESSONSTATUS.IN_PROGRESS, LESSONTASK.INFO)

            self.logging(f"Trying to scrape {self.current_lesson.url}")

            self.current_lesson.url = re.sub(
                r"[.,;:!?)]*$", "", self.current_lesson.url.strip()
            )

            if not self.current_lesson.url:
                self.logging("Lesson does not have a correct URL", LOGLEVEL.ERROR)
                self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.INFO)
                self.lesson_completed(error=True)

            self.headers = {"Authorization": f"Bearer {self.token}"}

            slug = self.extract_slug(self.current_lesson.url)

            self.current_lesson.slug = slug

            if not self.current_lesson.slug:
                self.logging(
                    "Cannot find Lesson Slug. Please that URL is correct.",
                    LOGLEVEL.ERROR,
                )
                self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.INFO)
                self.lesson_completed(error=True)

            self.wait_time(
                self.wait_time_between_reqs,
                lambda: self.get_lesson_info(self.current_lesson.slug),
            )

        else:
            self.logging(
                f"LessonWorker: Finished getting all lessons. Completed: {len(self.completed_lessons)} Errored: {len(self.errored_lessons)} "
            )
            # TODO send completed LESSONS and ERRORED LESSONS
            self.finished.emit()

    def extract_slug(self, input_str: str) -> str | None:
        """
        Extracts the slug from a lesson URL or returns the input
        if it's already a slug.

        Supports:
        - https://www.xyz.com/lesson/personal-finances
        - https://www.xyz.com/lessons/personal-finances#dialogue
        - personal-finances
        """
        # If it's a full URL, parse the path
        if input_str.startswith("http"):
            path = urlparse(input_str).path  # e.g., "/lesson/personal-finances"
            match = re.search(r"/lessons?/([^/?#]+)", path)
            return match.group(1) if match else None

        # If it's already a slug (e.g., "personal-finances")
        if re.fullmatch(r"[a-z0-9\-]+", input_str):
            return input_str

        return None

    def build_audio_url(self, path: str) -> str:

        if path.startswith(
            ("https://s3.amazonaws.com", "http://s3.amazonaws.com", self.audio_host_url)
        ):
            return path
        elif "expansionbygrammar" in path:
            match = re.search(r"chinesepod_(\d+)_", path)
            if match:
                grammar_id = match.group(1)
                return f"{self.audio_host_url}grammar/grammar_{grammar_id}/{grammar_id}/expansion/translation/mp3/{path}"
            else:
                return ""
        else:
            return f"{self.audio_host_url}{self.current_lesson.lesson_id}/{self.current_lesson.hash_code}/{path}"

    def create_networker(self, task_id, operation, url, cb, json=None):
        net_thread = QThread()
        networker = NetworkWorker(
            operation=operation,
            url=url,
            headers=self.headers,
            json=json,
        )
        task_id = f"{task_id}-{uuid.uuid4()}"
        networker.moveToThread(net_thread)
        networker.response.connect(cb)
        net_thread.started.connect(networker.do_work)
        networker.finished.connect(lambda: self.clean_up_manager.cleanup_task(task_id))
        net_thread.finished.connect(
            lambda: self.clean_up_manager.cleanup_task(task_id, True)
        )
        net_thread.start()
        self.clean_up_manager.add_task(
            task_id=task_id, thread=net_thread, worker=networker
        )

    def get_lesson_info(self, slug):
        self.logging(f"LessonWorker: Getting Lesson Info for - {slug}")

        self.create_networker(
            "lesson-info",
            "GET",
            url=f"{self.host_url}api/v2/lessons/get-lesson?slug={slug}",
            cb=self.lesson_info_received,
        )

    def parse_lesson_level(self, raw: str | None) -> LESSONLEVEL | None:
        LEVEL_MAP: dict[str, LESSONLEVEL] = {
            "newbie": LESSONLEVEL.NEWBIE,
            "beginner": LESSONLEVEL.NEWBIE,
            "elementary": LESSONLEVEL.ELEMENTARY,
            "intermediate": LESSONLEVEL.INTERMEDIATE,
            "upper intermediate": LESSONLEVEL.INTERMEDIATE,
            "advanced": LESSONLEVEL.ADVANCED,
        }
        normalized = raw.strip().lower()
        if normalized is None:
            return None
        return LEVEL_MAP.get(normalized)

    def lesson_info_received(self, res: NetworkResponse):
        self.logging("LessonWorker: Recieved Response for Lesson Info")
        if res.ok:
            lesson_info = res.data
            print(lesson_info)
            if "hash_code" in lesson_info and "id" in lesson_info:
                self.current_lesson.hash_code = lesson_info["hash_code"]
                self.current_lesson.level = self.parse_lesson_level(
                    lesson_info["level"]
                )
                self.current_lesson.lesson_id = lesson_info["id"]
                self.current_lesson.title = lesson_info["title"]

                self.task_complete.emit(
                    JobRef(
                        id=self.current_lesson.queue_id,
                        task=LESSONTASK.INFO,
                        status=JOBSTATUS.COMPLETE,
                    ),
                    {
                        "hash_code": self.current_lesson.hash_code,
                        "level": self.current_lesson.level,
                        "lesson_id": self.current_lesson.lesson_id,
                        "title": self.current_lesson.title,
                        "slug": lesson_info["slug"],
                        "lesson_audio": lesson_info["mp3_private"],
                        "dialogue_audio": lesson_info["mp3_dialogue"],
                    },
                )

                self.wait_time(self.wait_time_between_reqs, self.get_dialogue)
                self.send_status_update(LESSONSTATUS.COMPLETE, LESSONTASK.INFO)
                return
        else:
            self.logging(
                "Did not receive the Lesson Information. Skipping Lesson",
                LOGLEVEL.ERROR,
            )

            self.lesson_completed(error=True)
            self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.INFO)

    def get_dialogue(self):
        self.logging(
            f"Lesson: {self.current_lesson.title} - Getting Dialogue for Lesson"
        )
        self.send_status_update(LESSONSTATUS.IN_PROGRESS, LESSONTASK.DIALOGUE)
        self.create_networker(
            "dialogue",
            "GET",
            url=f"{self.host_url}api/v1/lessons/get-dialogue?lessonId={self.current_lesson.lesson_id}",
            cb=self.dialogue_received,
        )

    def dialogue_received(self, res: NetworkResponse):
        self.logging("LessonWorker: Received Response for Dialog")
        if res.ok:
            dialogue_payload = res.data

            if "dialogue" in dialogue_payload:
                for sentence in dialogue_payload["dialogue"]:
                    audio_path = sentence["audio"]
                    audio = self.build_audio_url(audio_path)
                    new_sent = Sentence(
                        chinese=sentence["s"],
                        english=sentence["en"],
                        pinyin=sentence["p"],
                        audio=audio,
                        level=self.current_lesson.level,
                        sent_type="dialogue",
                        lesson=(
                            self.current_lesson.title
                            if self.current_lesson.title
                            else ""
                        ),
                    )
                    self.current_lesson.lesson_parts.dialogue.append(new_sent)
                    self.current_lesson.lesson_parts.all_sentences.append(new_sent)

                self.logging(
                    f"Lesson: {self.current_lesson.title} - Sending {len(self.current_lesson.lesson_parts.dialogue)} Dialogue Sentences"
                )
                self.task_complete.emit(
                    JobRef(
                        id=self.current_lesson.queue_id,
                        task=LESSONTASK.DIALOGUE,
                        status=JOBSTATUS.COMPLETE,
                    ),
                    {"sentences": self.current_lesson.lesson_parts.dialogue},
                )

            else:
                self.logging(
                    f"Lesson - {self.current_lesson.title}  doesnt have a Dialogue Section",
                    LOGLEVEL.WARN,
                )
            self.send_status_update(LESSONSTATUS.COMPLETE, LESSONTASK.DIALOGUE)

        else:

            self.logging(
                f"Error receiving Dialogue - {res.status} -{res.message}",
                LOGLEVEL.WARN,
            )
            self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.DIALOGUE)
        self.wait_time(self.wait_time_between_reqs, self.get_lesson_vocab)

    def get_lesson_vocab(self):
        self.logging("LessonWorker: Getting Vocabulary for Lesson")
        self.send_status_update(LESSONSTATUS.IN_PROGRESS, LESSONTASK.VOCAB)
        self.create_networker(
            "vocab",
            "GET",
            url=f"{self.host_url}api/v2/lessons/get-vocab?lessonId={self.current_lesson.lesson_id}",
            cb=self.vocab_received,
        )

    def vocab_received(self, res: NetworkResponse):
        self.logging("LessonWorker: Received Vocab Response for Lesson")
        if res.ok:
            vocab = res.data

            if isinstance(vocab, list) and vocab:
                for word in vocab:
                    audio_path = word["audio"]
                    audio = self.build_audio_url(audio_path)
                    new_word = Word(
                        chinese=word["s"],
                        definition=word["en"],
                        pinyin=word["p"],
                        audio=audio,
                        lesson=self.current_lesson.title,
                    )
                    self.current_lesson.lesson_parts.vocab.append(new_word)
                self.logging(
                    f"Lesson: {self.current_lesson.title} - Sending {len(self.current_lesson.lesson_parts.vocab)} Vocabulary Words"
                )

                self.task_complete.emit(
                    JobRef(
                        id=self.current_lesson.queue_id,
                        task=LESSONTASK.VOCAB,
                        status=JOBSTATUS.COMPLETE,
                    ),
                    {"words": self.current_lesson.lesson_parts.vocab},
                )
            else:
                self.logging(
                    f"Lesson {self.current_lesson.title} doesnt have Vocabulary Words",
                    LOGLEVEL.WARN,
                )
                self.current_lesson.status = LESSONSTATUS.IN_PROGRESS

            self.send_status_update(LESSONSTATUS.COMPLETE, LESSONTASK.VOCAB)
        else:
            self.logging(
                f"LessonWorker: Error recieving Vocab - {res.status} - {res.message}",
                LOGLEVEL.WARN,
            )

            self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.VOCAB)

        self.wait_time(self.wait_time_between_reqs, self.get_expansion)

    def get_expansion(self):
        self.logging("LessonWorker: Getting Expansion for Lesson")
        self.send_status_update(LESSONSTATUS.IN_PROGRESS, LESSONTASK.EXPANSION)
        self.create_networker(
            "expansion",
            "GET",
            f"{self.host_url}api/v1/lessons/get-expansion?lessonId={self.current_lesson.lesson_id}",
            cb=self.expansion_received,
        )

    def expansion_received(self, res: NetworkResponse):
        self.logging("LessonWorker: Received Expansion Response")
        if res.ok:
            expansion_payload = res.data
            if expansion_payload:
                for section in expansion_payload:
                    for sentence in section["examples"]:
                        audio_path = sentence["audio"]
                        audio = self.build_audio_url(audio_path)
                        new_sent = Sentence(
                            chinese=sentence["s"],
                            english=sentence["en"],
                            pinyin=sentence["p"],
                            audio=audio,
                            level=self.current_lesson.level,
                            sent_type="expansion",
                            lesson=(
                                self.current_lesson.title
                                if self.current_lesson.title
                                else ""
                            ),
                        )
                        self.current_lesson.lesson_parts.expansion.append(new_sent)
                        self.current_lesson.lesson_parts.all_sentences.append(new_sent)

                self.logging(
                    f"Lesson: {self.current_lesson.title} - Sending {len(self.current_lesson.lesson_parts.expansion)} Expansion Sentences"
                )

                self.task_complete.emit(
                    JobRef(
                        id=self.current_lesson.queue_id,
                        task=LESSONTASK.EXPANSION,
                        status=JOBSTATUS.COMPLETE,
                    ),
                    {"sentences": self.current_lesson.lesson_parts.expansion},
                )

            else:
                self.logging(
                    f"Lesson - {self.current_lesson.title} doesnt have a Expansion Section",
                    LOGLEVEL.WARN,
                )
            self.send_status_update(LESSONSTATUS.COMPLETE, LESSONTASK.EXPANSION)
        else:
            self.logging(
                f"Error recieving Expansion - {res.status} - {res.message} ",
                LOGLEVEL.ERROR,
            )
            self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.EXPANSION)

        self.wait_time(self.wait_time_between_reqs, self.get_grammar)

    def get_grammar(self):
        self.logging("LessonWorker: Getting Grammar for Lesson")
        self.send_status_update(LESSONSTATUS.IN_PROGRESS, LESSONTASK.GRAMMAR)
        self.g_net_thread = QThread()
        self.create_networker(
            "grammar",
            "GET",
            f"{self.host_url}api/v1/lessons/get-grammar?lessonId={self.current_lesson.lesson_id}",
            cb=self.grammar_received,
        )

    def grammar_received(self, res: NetworkResponse):
        self.logging("LessonWorker: Received Grammar Response for Lesson")
        if res.ok:
            grammar_payload = res.data
            grammar = []

            if grammar_payload:
                for section in grammar_payload:

                    grammar_point = GrammarPoint(
                        name=section["grammar"]["name"],
                        explanation=section["grammar"]["introduction"],
                    )
                    for sentence in section["examples"]:

                        audio_path = sentence["audio"]
                        audio = self.build_audio_url(audio_path)
                        new_sent = Sentence(
                            chinese=sentence["s"],
                            english=sentence["en"],
                            pinyin=sentence["p"],
                            audio=audio,
                            level=self.current_lesson.level,
                            sent_type="grammar",
                            lesson=(
                                self.current_lesson.title
                                if self.current_lesson.title
                                else ""
                            ),
                        )
                        grammar.append(new_sent)
                        grammar_point.examples.append(new_sent)
                        self.current_lesson.lesson_parts.all_sentences.append(new_sent)
                    self.current_lesson.lesson_parts.grammar.append(grammar_point)
                self.logging(
                    f"Lesson: {self.current_lesson.title} - Sending {len(grammar)} Grammar Sentences"
                )
                self.task_complete.emit(
                    JobRef(
                        id=self.current_lesson.queue_id,
                        task=LESSONTASK.GRAMMAR,
                        status=JOBSTATUS.COMPLETE,
                    ),
                    {
                        "sentences": grammar,
                        "grammar": self.current_lesson.lesson_parts.grammar,
                    },
                )

            else:
                self.logging(
                    f"Lesson - {self.current_lesson.title} doesnt have a Grammar Section",
                    LOGLEVEL.WARN,
                )
            self.send_status_update(LESSONSTATUS.COMPLETE, LESSONTASK.GRAMMAR)
        else:
            self.logging(
                f"LessonWorker: Error recieving Grammar - {res.status} - {res.message}",
                LOGLEVEL.ERROR,
            )
            self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.GRAMMAR)

        self.wait_time(self.wait_time_between_reqs, self.check_lesson_complete)

    def check_lesson_complete(self):
        if self.current_lesson_checked or not self.current_lesson.lesson_id:
            return
        self.current_lesson_checked = True
        self.logging(
            f"Trying to check Complete for Lesson for {self.current_lesson.lesson_id}"
        )
        self.current_lesson.task = LESSONTASK.CHECK
        self.send_status_update(LESSONSTATUS.IN_PROGRESS, LESSONTASK.CHECK)
        self.create_networker(
            "toggle-studied",
            "POST",
            url=f"{self.host_url}api/v1/dashboard/toggle-studied",
            json={"lessonId": f"{self.current_lesson.lesson_id}", "status": True},
            cb=self.received_lesson_complete,
        )

    def received_lesson_complete(self, res: NetworkResponse):
        if res.ok:
            self.logging(
                f"Lesson: {self.current_lesson.title} - Successfully Marked Lesson Complete."
            )
        else:
            self.logging(
                f"Lesson: {self.current_lesson.title} - Failed to mark complete",
                LOGLEVEL.WARN,
            )
        QTimer.singleShot(1000, self.lesson_completed)

    def lesson_completed(self, error=False):
        if error:
            self.errored_lessons.append(self.current_lesson)

        else:
            parts = self.current_lesson.lesson_parts
            if parts.dialogue and parts.all_sentences:
                if not self.current_lesson_checked:
                    self.check_lesson_complete()
                    return
                else:
                    self.send_status_update(LESSONSTATUS.COMPLETE, LESSONTASK.CHECK)
                    self.task_complete.emit(
                        JobRef(
                            id=self.current_lesson.queue_id,
                            task=LESSONTASK.CHECK,
                            status=JOBSTATUS.COMPLETE,
                        ),
                        {},
                    )
                    self.logging(f"Completed Lesson - {self.current_lesson.title}")
                    self.completed_lessons.append(self.current_lesson)

        wait_time = randint(10, 90) if self.lesson_list else 0
        self.logging(
            f"LessonWorker: Waiting {wait_time} seconds before scraping next lesson."
        )
        QTimer.singleShot(wait_time * 1000, self.get_next_lesson)
