import re
import time
from collections import deque
from random import randint
from urllib.parse import urlparse

from PySide6.QtCore import QMutexLocker, QObject, QThread, Signal

from keys import keys
from models.dictionary import Dialogue, Sentence, Word
from services.network import NetworkWorker, SessionManager


class LessonScraperWorkerV2(QObject):
    finished = Signal()
    send_sents_sig = Signal(object)
    send_words_sig = Signal(list)
    send_dialogue = Signal(object, object)
    lesson_done = Signal(str, str)

    def __init__(self, web_driver, lesson_list, mutex, wait_condition, parent_thread):
        super().__init__()
        self.web_driver = web_driver
        self.lesson_list = deque(lesson_list)
        self._mutex = mutex
        self._wait_condition = wait_condition
        self.parent_thread = parent_thread
        self.temp_file_paths = []
        self.session = SessionManager()
        self.host_url = keys["url"]
        self.audio_host_url = keys["audio_host"]
        self.token = None

    def do_work(self):
        self.get_next_lesson()

    def get_next_lesson(self):
        print("starting since")
        if self.lesson_list:
            with QMutexLocker(self._mutex):
                if self.parent_thread._stop:
                    self.finished.emit()

                while self.parent_thread._paused:
                    self._wait_condition.wait(self._mutex)
            c_lesson = self.lesson_list.popleft()

            if not self.token:
                try:
                    self.web_driver.find_bearer()
                    token = self.web_driver.get_bearer()
                    # TODO save token to settings?
                    if not token:
                        raise RuntimeError("Bearer token is None after login flow.")
                    self.token = token
                except RuntimeError as e:
                    print(e)
                except Exception as e:
                    print(e)

            self.lesson_id = self.web_driver.find_lesson_id(c_lesson)
            self.web_driver.check_complete_lesson()
            if not self.lesson_id:
                return

            print("Lesson Id is ", self.lesson_id)

            self.headers = {"Authorization": self.token}
            slug = self.extract_slug(c_lesson)

            if not slug:
                return

            self.get_lesson_info(slug)
        else:
            print("Finished getting all lessons.")
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
            return f"{self.audio_host_url}{self.lesson_id}/{self.hash_code}/{path}"

    def get_lesson_info(self, slug):
        self.lesi_net_thread = QThread()
        self.lesi_net = NetworkWorker(
            self.session,
            "GET",
            f"{self.host_url}api/v2/lessons/get-lesson?slug={slug}",
            headers=self.headers,
        )
        self.lesi_net_thread.start()
        self.lesi_net.moveToThread(self.lesi_net_thread)
        self.lesi_net.response_sig.connect(self.lesson_info_received)
        self.lesi_net.do_work()
        self.lesi_net.finished.connect(self.lesi_net_thread.deleteLater)

    def lesson_info_received(self, status, payload):
        lesson_info = payload.json()

        if "hash_code" in lesson_info and "id" in lesson_info:
            self.hash_code = lesson_info["hash_code"]
            self.lesson_level = lesson_info["level"]
            self.lesson_id = lesson_info["id"]
            self.lesson_title = lesson_info["title"]

            dialogue_audio = Dialogue(
                title=f"{self.lesson_level} - {self.lesson_title} - Dialogue",
                audio_type="dialogue",
                audio=lesson_info["mp3_dialogue"],
                level=self.lesson_level,
                lesson=self.lesson_title,
            )

            lesson_audio = Dialogue(
                title=f"{self.lesson_level} - {self.lesson_title} - Lesson",
                audio_type="lesson",
                audio=lesson_info["mp3_private"],
                level=self.lesson_level,
                lesson=self.lesson_title,
            )

            self.send_dialogue.emit(lesson_audio, dialogue_audio)
            self.get_dialogue()
        else:
            print("Error getting information for the lesson")
            self.lesson_completed()

    def get_dialogue(self):
        self.d_net_thread = QThread()
        self.dialogue_net = NetworkWorker(
            self.session,
            "GET",
            f"{self.host_url}api/v1/lessons/get-dialogue?lessonId={self.lesson_id}",
            headers=self.headers,
        )
        self.d_net_thread.start()
        self.dialogue_net.moveToThread(self.d_net_thread)
        self.dialogue_net.response_sig.connect(self.dialogue_received)
        self.dialogue_net.do_work()
        self.dialogue_net.finished.connect(self.d_net_thread.deleteLater)

    def dialogue_received(self, status, payload):
        dialogue_payload = payload.json()
        dialogue = []

        if "dialogue" in dialogue_payload:
            for sentence in dialogue_payload["dialogue"]:
                audio_path = sentence["audio"]
                audio = self.build_audio_url(audio_path)
                new_sent = Sentence(
                    chinese=sentence["s"],
                    english=sentence["en"],
                    pinyin=sentence["p"],
                    audio=audio,
                    level=self.lesson_level,
                    sent_type="dialogue",
                    lesson=self.lesson_title if self.lesson_title else "",
                )
                dialogue.append(new_sent)
            print(f"Sending {len(dialogue)} Dialogue Sentences")
        else:
            print(f"Lesson - {self.lesson_title} doesnt have a Dialogue Section")
        self.send_sents_sig.emit(dialogue)

        self.get_lesson_vocab()

    def get_lesson_vocab(self):
        self.v_net_thread = QThread()
        self.vocab_net = NetworkWorker(
            self.session,
            "GET",
            f"{self.host_url}api/v2/lessons/get-vocab?lessonId={self.lesson_id}",
            headers=self.headers,
        )
        self.v_net_thread.start()
        self.vocab_net.moveToThread(self.v_net_thread)
        self.vocab_net.response_sig.connect(self.vocab_received)
        self.vocab_net.do_work()
        self.vocab_net.finished.connect(self.v_net_thread.deleteLater)

    def vocab_received(self, status, payload):
        vocab = payload.json()
        words = []
        if isinstance(vocab, list) and vocab:
            for word in vocab:
                audio_path = word["audio"]
                audio = self.build_audio_url(audio_path)
                new_word = Word(
                    chinese=word["s"],
                    definition=word["en"],
                    pinyin=word["p"],
                    audio=audio,
                )
                words.append(new_word)
            print(f"Sending {len(words)} Vocabulary Words")
        else:
            print(f"Lesson - {self.lesson_title} doesnt have Vocabulary Words")
        self.send_words_sig.emit(words)
        self.get_expansion()

    def get_expansion(self):
        self.e_net_thread = QThread()
        self.expansion_net = NetworkWorker(
            self.session,
            "GET",
            f"{self.host_url}api/v1/lessons/get-expansion?lessonId={self.lesson_id}",
            headers=self.headers,
        )
        self.e_net_thread.start()
        self.expansion_net.moveToThread(self.e_net_thread)
        self.expansion_net.response_sig.connect(self.expansion_received)
        self.expansion_net.do_work()
        self.expansion_net.finished.connect(self.e_net_thread.deleteLater)

    def expansion_received(self, status, payload):
        expansion_payload = payload.json()
        expansion = []

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
                        level=self.lesson_level,
                        sent_type="expansion",
                        lesson=self.lesson_title if self.lesson_title else "",
                    )
                    expansion.append(new_sent)

            print(f"Sending {len(expansion)} Expansion Sentences")
        else:
            print(f"Lesson - {self.lesson_title} doesnt have a Expansion Section")
        self.send_sents_sig.emit(expansion)
        self.get_grammar()

    def get_grammar(self):
        self.g_net_thread = QThread()
        self.grammer_net = NetworkWorker(
            self.session,
            "GET",
            f"{self.host_url}api/v1/lessons/get-grammar?lessonId={self.lesson_id}",
            headers=self.headers,
        )
        self.g_net_thread.start()
        self.grammer_net.moveToThread(self.g_net_thread)
        self.grammer_net.response_sig.connect(self.grammer_received)
        self.grammer_net.do_work()
        self.grammer_net.finished.connect(self.g_net_thread.deleteLater)

    def grammer_received(self, status, payload):
        grammar_payload = payload.json()
        grammar = []
        if grammar_payload:
            for section in grammar_payload:
                for sentence in section["examples"]:

                    audio_path = sentence["audio"]
                    audio = self.build_audio_url(audio_path)
                    new_sent = Sentence(
                        chinese=sentence["s"],
                        english=sentence["en"],
                        pinyin=sentence["p"],
                        audio=audio,
                        level=self.lesson_level,
                        sent_type="grammar",
                        lesson=self.lesson_title if self.lesson_title else "",
                    )
                    grammar.append(new_sent)
            print(f"Sending {len(grammar)} Grammar Sentences")
        else:
            print(f"Lesson - {self.lesson_title} doesnt have a Grammar Section")
        self.send_sents_sig.emit(grammar)
        self.lesson_completed()

    def lesson_completed(self):
        self.lesson_done.emit(self.lesson_title, self.lesson_level)
        print(f"Completed Lesson - {self.lesson_title}")
        print("Trying to get next lesson")
        time.sleep(randint(6, 15))
        self.get_next_lesson()
