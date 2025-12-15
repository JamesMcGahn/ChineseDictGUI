import re
from collections import deque
from random import randint
from urllib.parse import urlparse

from PySide6.QtCore import QMutexLocker, QThread, QTimer, Signal, Slot

from base import QWorkerBase
from base.enums import LESSONLEVEL, LESSONSTATUS, LESSONTASK, LOGLEVEL
from keys import keys
from models.dictionary import GrammarPoint, Lesson, LessonAudio, Sentence, Word
from services.network import NetworkWorker


class LessonScraperWorkerV2(QWorkerBase):
    finished = Signal()
    send_sents_sig = Signal(object)
    send_words_sig = Signal(list)
    send_dialogue = Signal(object, object)
    lesson_done = Signal(object)
    request_token = Signal()

    def __init__(
        self, lesson_list, mutex, wait_condition, parent_thread, transcribe_lesson
    ):
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
        self.transcribe_lesson = transcribe_lesson

        self.current_lesson: Lesson | None = None
        self.completed_lessons = []
        self.errored_lessons = []

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

    def get_next_lesson(self):
        self.current_lesson = None
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

            self.current_lesson = self.lesson_list.popleft()
            self.current_lesson.status = LESSONSTATUS.IN_PROGRESS
            self.current_lesson.task = LESSONTASK.INFO

            self.logging(f"Trying to scrape {self.current_lesson.url}")

            self.current_lesson.url = re.sub(
                r"[.,;:!?)]*$", "", self.current_lesson.url.strip()
            )

            if not self.current_lesson.url:
                self.logging("Lesson does not have a correct URL", LOGLEVEL.ERROR)
                self.current_lesson.status = LESSONSTATUS.ERROR
                self.lesson_completed(error=True)

            self.headers = {"Authorization": f"Bearer {self.token}"}
            slug = self.extract_slug(self.current_lesson.url)
            self.current_lesson.slug = slug
            if not self.current_lesson.slug:
                self.logging(
                    "Cannot find Lesson Slug. Please that URL is correct.",
                    LOGLEVEL.ERROR,
                )
                self.current_lesson.status = LESSONSTATUS.ERROR
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

    def check_lesson_complete(self):
        self.current_lesson.task = LESSONTASK.CHECK
        if not self.current_lesson.lesson_id:
            return
        self.logging(
            f"Trying to check Complete for Lesson for {self.current_lesson.lesson_id}"
        )
        self.check_lesson_thread = QThread()
        self.check_lesson_net = NetworkWorker(
            "POST",
            f"{self.host_url}api/v1/dashboard/toggle-studied",
            headers=self.headers,
            json={"lessonId": f"{self.current_lesson.lesson_id}", "status": True},
        )
        self.check_lesson_net.moveToThread(self.check_lesson_thread)
        self.check_lesson_thread.start()

        self.check_lesson_net.response_sig.connect(self.received_lesson_complete)
        self.check_lesson_net.error_sig.connect(self.received_lesson_complete)
        self.check_lesson_net.do_work()
        self.check_lesson_net.finished.connect(self.check_lesson_thread.deleteLater)

    def received_lesson_complete(self, status, payload, status_code=None):
        if status == "success":
            self.logging(
                f"Lesson: {self.current_lesson.title} - Successfully Marked Lesson Complete."
            )
        else:
            print(
                f"Lesson: {self.current_lesson.title} - Failed to mark complete",
                LOGLEVEL.WARN,
            )
        self.lesson_completed()

    def get_lesson_info(self, slug):
        self.logging(f"LessonWorker: Getting Lesson Info for - {slug}")
        self.lesi_net_thread = QThread()
        self.lesi_net = NetworkWorker(
            "GET",
            f"{self.host_url}api/v2/lessons/get-lesson?slug={slug}",
            headers=self.headers,
        )
        self.lesi_net_thread.start()
        self.lesi_net.moveToThread(self.lesi_net_thread)
        self.lesi_net.response_sig.connect(self.lesson_info_received)
        self.lesi_net.do_work()
        self.lesi_net.finished.connect(self.lesi_net_thread.deleteLater)

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

    def lesson_info_received(self, status, payload):
        self.logging("LessonWorker: Recieved Response for Lesson Info")
        if status == "error":
            self.logging(
                "Did not receive the Lesson Information. Skipping Lesson",
                LOGLEVEL.ERROR,
            )
            self.current_lesson.status = LESSONSTATUS.ERROR
            self.lesson_completed()
            return
        lesson_info = payload.json()

        if "hash_code" in lesson_info and "id" in lesson_info:
            self.current_lesson.hash_code = lesson_info["hash_code"]
            self.current_lesson.level = self.parse_lesson_level(lesson_info["level"])
            self.current_lesson.lesson_id = lesson_info["id"]
            self.current_lesson.title = lesson_info["title"]

            dialogue_audio = LessonAudio(
                title=f"{self.current_lesson.level} - {self.current_lesson.title} - Dialogue",
                audio_type="dialogue",
                audio=lesson_info["mp3_dialogue"],
                level=self.current_lesson.level,
                lesson=self.current_lesson.title,
                transcribe=False,
            )

            lesson_audio = LessonAudio(
                title=f"{self.current_lesson.level} - {self.current_lesson.title} - Lesson",
                audio_type="lesson",
                audio=lesson_info["mp3_private"],
                level=self.current_lesson.level,
                lesson=self.current_lesson.title,
                transcribe=self.transcribe_lesson,
            )

            self.send_dialogue.emit(lesson_audio, dialogue_audio)
            self.wait_time(self.wait_time_between_reqs, self.get_dialogue)
            self.current_lesson.lesson_parts.lesson_audios.append(dialogue_audio)
            self.current_lesson.lesson_parts.lesson_audios.append(lesson_audio)
        else:
            self.current_lesson.status = LESSONSTATUS.ERROR
            self.logging("Error getting information for the lesson", LOGLEVEL.ERROR)
            self.lesson_completed()

    def get_dialogue(self):
        self.logging(
            f"Lesson: {self.current_lesson.title} - Getting Dialogue for Lesson"
        )
        self.current_lesson.task = LESSONTASK.DIALOGUE
        self.d_net_thread = QThread()
        self.dialogue_net = NetworkWorker(
            "GET",
            f"{self.host_url}api/v1/lessons/get-dialogue?lessonId={self.current_lesson.lesson_id}",
            headers=self.headers,
        )
        self.d_net_thread.start()
        self.dialogue_net.moveToThread(self.d_net_thread)
        self.dialogue_net.response_sig.connect(self.dialogue_received)
        self.dialogue_net.error_sig.connect(self.dialogue_received)
        self.dialogue_net.do_work()
        self.dialogue_net.finished.connect(self.d_net_thread.deleteLater)

    def dialogue_received(self, status, payload, status_code=None):
        self.logging("LessonWorker: Received Response for Dialog")
        if status == "error":
            self.logging(f"Error recieving Dialog - {status_code}", LOGLEVEL.WARN)
            self.current_lesson.status = LESSONSTATUS.ERROR
            self.wait_time(self.wait_time_between_reqs, self.get_lesson_vocab)
            return
        dialogue_payload = payload.json()

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
                        self.current_lesson.title if self.current_lesson.title else ""
                    ),
                )
                self.current_lesson.lesson_parts.dialogue.append(new_sent)
                self.current_lesson.lesson_parts.all_sentences.append(new_sent)
            self.logging(
                f"Lesson: {self.current_lesson.title} - Sending {len(self.current_lesson.lesson_parts.dialogue)} Dialogue Sentences"
            )
        else:
            self.logging(
                f"Lesson - {self.current_lesson.title}  doesnt have a Dialogue Section",
                LOGLEVEL.WARN,
            )
            self.current_lesson.status = LESSONSTATUS.IN_PROGRESS
        self.send_sents_sig.emit(self.current_lesson.lesson_parts.dialogue)
        self.wait_time(self.wait_time_between_reqs, self.get_lesson_vocab)

    def get_lesson_vocab(self):
        self.logging("LessonWorker: Getting Vocabulary for Lesson")
        self.current_lesson.task = LESSONTASK.VOCAB
        self.current_lesson.status = LESSONSTATUS.IN_PROGRESS
        self.v_net_thread = QThread()
        self.vocab_net = NetworkWorker(
            "GET",
            f"{self.host_url}api/v2/lessons/get-vocab?lessonId={self.current_lesson.lesson_id}",
            headers=self.headers,
        )
        self.v_net_thread.start()
        self.vocab_net.moveToThread(self.v_net_thread)
        self.vocab_net.response_sig.connect(self.vocab_received)
        self.vocab_net.error_sig.connect(self.vocab_received)
        self.vocab_net.do_work()
        self.vocab_net.finished.connect(self.v_net_thread.deleteLater)

    def vocab_received(self, status, payload, status_code=None):
        self.logging("LessonWorker: Received Vocab Response for Lesson")
        if status == "error":
            self.logging(
                f"LessonWorker: Error recieving Vocab - {status_code}", LOGLEVEL.WARN
            )
            self.wait_time(self.wait_time_between_reqs, self.get_expansion)
            self.current_lesson.status = LESSONSTATUS.ERROR
            return

        vocab = payload.json()

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
        else:
            self.logging(
                f"Lesson {self.current_lesson.title} doesnt have Vocabulary Words",
                LOGLEVEL.WARN,
            )
            self.current_lesson.status = LESSONSTATUS.IN_PROGRESS
        self.send_words_sig.emit(self.current_lesson.lesson_parts.vocab)
        self.wait_time(self.wait_time_between_reqs, self.get_expansion)

    def get_expansion(self):
        self.logging("LessonWorker: Getting Expansion for Lesson")
        self.current_lesson.task = LESSONTASK.EXPANSION
        self.current_lesson.status = LESSONSTATUS.IN_PROGRESS
        self.e_net_thread = QThread()
        self.expansion_net = NetworkWorker(
            "GET",
            f"{self.host_url}api/v1/lessons/get-expansion?lessonId={self.current_lesson.lesson_id}",
            headers=self.headers,
        )
        self.e_net_thread.start()
        self.expansion_net.moveToThread(self.e_net_thread)
        self.expansion_net.response_sig.connect(self.expansion_received)
        self.expansion_net.error_sig.connect(self.expansion_received)
        self.expansion_net.do_work()
        self.expansion_net.finished.connect(self.e_net_thread.deleteLater)

    def expansion_received(self, status, payload, status_code=None):
        self.logging("LessonWorker: Received Expansion Response")
        if status == "error":
            self.logging(f"Error recieving Expansion - {status_code} ", LOGLEVEL.ERROR)
            self.wait_time(self.wait_time_between_reqs, self.get_grammar)
            self.current_lesson.status = LESSONSTATUS.ERROR
            return

        expansion_payload = payload.json()

        if expansion_payload and not status == "error":
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
        else:
            self.logging(
                f"Lesson - {self.current_lesson.title} doesnt have a Expansion Section",
                LOGLEVEL.WARN,
            )
            self.current_lesson.status = LESSONSTATUS.IN_PROGRESS
        self.send_sents_sig.emit(self.current_lesson.lesson_parts.expansion)
        self.wait_time(self.wait_time_between_reqs, self.get_grammar)

    def get_grammar(self):
        self.logging("LessonWorker: Getting Grammar for Lesson")
        self.current_lesson.task = LESSONTASK.GRAMMAR
        self.current_lesson.status = LESSONSTATUS.IN_PROGRESS
        self.g_net_thread = QThread()
        self.grammer_net = NetworkWorker(
            "GET",
            f"{self.host_url}api/v1/lessons/get-grammar?lessonId={self.current_lesson.lesson_id}",
            headers=self.headers,
        )
        self.g_net_thread.start()
        self.grammer_net.moveToThread(self.g_net_thread)
        self.grammer_net.response_sig.connect(self.grammar_received)
        self.grammer_net.error_sig.connect(self.grammar_received)
        self.grammer_net.do_work()
        self.grammer_net.finished.connect(self.g_net_thread.deleteLater)

    def grammar_received(self, status, payload, status_code=None):
        self.logging("LessonWorker: Received Grammar Response for Lesson")
        if status == "error":
            self.logging(
                f"LessonWorker: Error recieving Grammar - {status_code}", LOGLEVEL.ERROR
            )
            self.lesson_completed()
            return
        grammar_payload = payload.json()
        grammar = []

        if grammar_payload and not status == "error":
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
        else:
            self.logging(
                f"Lesson - {self.current_lesson.title} doesnt have a Grammar Section",
                LOGLEVEL.WARN,
            )
            self.current_lesson.status = LESSONSTATUS.IN_PROGRESS
        self.send_sents_sig.emit(grammar)
        self.lesson_completed()

    def lesson_completed(self, error=False):
        if error:
            self.errored_lessons.append(self.current_lesson)

        else:
            parts = self.current_lesson.lesson_parts
            if parts.lesson_audios and parts.dialogue and parts.all_sentences:
                if self.current_lesson.task != LESSONTASK.CHECK:
                    self.check_lesson_complete()
                    return
                else:
                    self.lesson_done.emit(self.current_lesson)
                    self.logging(f"Completed Lesson - {self.current_lesson.title}")
                    self.completed_lessons.append(self.current_lesson)

        wait_time = randint(10, 90) if self.lesson_list else 0
        self.logging(
            f"LessonWorker: Waiting {wait_time} seconds before scraping next lesson."
        )
        QTimer.singleShot(wait_time * 1000, self.get_next_lesson)
