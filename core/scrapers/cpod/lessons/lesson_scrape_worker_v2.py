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
from models.core import LessonTaskPayload
from models.dictionary import GrammarPoint, Lesson, LessonAudio, Sentence, Word
from models.services import JobRef, NetworkResponse
from services.network import NetworkWorker

from .lesson_parsers import (
    extract_slug,
    parse_dialogue,
    parse_expansion,
    parse_grammar,
    parse_lesson_info,
    parse_vocab,
)


class LessonScraperWorkerV2(QWorkerBase):
    finished = Signal()
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

        self.task_map = {
            LESSONTASK.INFO: self.get_lesson_info,
            LESSONTASK.DIALOGUE: self.get_dialogue,
            LESSONTASK.VOCAB: self.get_lesson_vocab,
            LESSONTASK.EXPANSION: self.get_expansion,
            LESSONTASK.GRAMMAR: self.get_grammar,
            LESSONTASK.CHECK: self.check_lesson_complete,
        }

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

            slug = extract_slug(self.current_lesson.url)

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
                lambda: self.dispatch(LESSONTASK.INFO),
            )

        else:
            self.logging(
                f"LessonWorker: Finished getting all lessons. Completed: {len(self.completed_lessons)} Errored: {len(self.errored_lessons)} "
            )
            # TODO send completed LESSONS and ERRORED LESSONS
            self.finished.emit()

    def dispatch(self, task: LESSONTASK):
        self.current_lesson.task = task
        self.send_status_update(LESSONSTATUS.IN_PROGRESS, task)
        handler = self.task_map[task]
        handler()

    def get_next_task(self, current_task: LESSONTASK) -> LESSONTASK | None:
        TASK_FLOW = [
            LESSONTASK.INFO,
            LESSONTASK.DIALOGUE,
            LESSONTASK.VOCAB,
            LESSONTASK.EXPANSION,
            LESSONTASK.GRAMMAR,
            LESSONTASK.CHECK,
        ]
        try:
            index = TASK_FLOW.index(current_task)
            return TASK_FLOW[index + 1]
        except (ValueError, IndexError):
            return None

    def on_task_complete(self, task, success=True):
        if not success:
            # TODO error handling for each task
            self.logging(f"Task {task} failed", LOGLEVEL.ERROR)
            # self.handle_error(task)
            return

        next_task = self.get_next_task(task)
        self.send_status_update(LESSONSTATUS.COMPLETE, task)

        if next_task:
            self.wait_time(
                self.wait_time_between_reqs, lambda: self.dispatch(next_task)
            )
        else:
            self.lesson_completed()

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
        networker.finished.connect(
            lambda tid=task_id: self.clean_up_manager.cleanup_task(tid)
        )
        net_thread.finished.connect(
            lambda tid=task_id: self.clean_up_manager.cleanup_task(tid, True)
        )
        net_thread.start()
        self.clean_up_manager.add_task(
            task_id=task_id, thread=net_thread, worker=networker
        )

    def get_lesson_info(self):
        slug = self.current_lesson.slug
        self.logging(f"LessonWorker: Getting Lesson Info for - {slug}")

        self.create_networker(
            "lesson-info",
            "GET",
            url=f"{self.host_url}api/v2/lessons/get-lesson?slug={slug}",
            cb=self.lesson_info_received,
        )

    def lesson_info_received(self, res: NetworkResponse):
        self.logging("LessonWorker: Recieved Response for Lesson Info")
        if res.ok:
            payload = parse_lesson_info(res.data)
            if payload.lesson_info is None:
                self.lesson_completed(error=True)
                return
            self.current_lesson.hash_code = payload.lesson_info.hash_code
            self.current_lesson.level = payload.lesson_info.level
            self.current_lesson.lesson_id = payload.lesson_info.lesson_id
            self.current_lesson.title = payload.lesson_info.title

            self.task_complete.emit(
                JobRef(
                    id=self.current_lesson.queue_id,
                    task=LESSONTASK.INFO,
                    status=JOBSTATUS.COMPLETE,
                ),
                payload,
            )
            self.on_task_complete(LESSONTASK.INFO, True)
        else:
            self.logging(
                "Did not receive the Lesson Information. Skipping Lesson",
                LOGLEVEL.ERROR,
            )
            # TODO MOVE ERROR TO DISPATCH
            self.lesson_completed(error=True)
            self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.INFO)

    def get_dialogue(self):
        self.logging(
            f"Lesson: {self.current_lesson.title} - Getting Dialogue for Lesson"
        )
        self.create_networker(
            "dialogue",
            "GET",
            url=f"{self.host_url}api/v1/lessons/get-dialogue?lessonId={self.current_lesson.lesson_id}",
            cb=self.dialogue_received,
        )

    def dialogue_received(self, res: NetworkResponse):
        self.logging("LessonWorker: Received Response for Dialog")
        if res.ok:
            payload = parse_dialogue(lesson=self.current_lesson, res_data=res.data)

            if not payload.sentences:
                self.logging(
                    f"Lesson - {self.current_lesson.title}  doesnt have a Dialogue Section",
                    LOGLEVEL.WARN,
                )

            self.current_lesson.lesson_parts.dialogue.extend(payload.sentences)
            self.current_lesson.lesson_parts.all_sentences.extend(payload.sentences)

            self.logging(
                f"Lesson: {self.current_lesson.title} - Sending {len(payload.sentences)} Dialogue Sentences"
            )
            self.task_complete.emit(
                JobRef(
                    id=self.current_lesson.queue_id,
                    task=LESSONTASK.DIALOGUE,
                    status=JOBSTATUS.COMPLETE,
                ),
                payload,
            )
        else:
            self.logging(
                f"Error receiving Dialogue - {res.status} -{res.message}",
                LOGLEVEL.WARN,
            )
            self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.DIALOGUE)

        self.on_task_complete(LESSONTASK.DIALOGUE, True)
        # TODO ERROR HANDLING

    def get_lesson_vocab(self):
        self.logging("LessonWorker: Getting Vocabulary for Lesson")
        self.create_networker(
            "vocab",
            "GET",
            url=f"{self.host_url}api/v2/lessons/get-vocab?lessonId={self.current_lesson.lesson_id}",
            cb=self.vocab_received,
        )

    def vocab_received(self, res: NetworkResponse):
        self.logging("LessonWorker: Received Vocab Response for Lesson")
        if res.ok:
            payload = parse_vocab(lesson=self.current_lesson, res_data=res.data)

            if not payload.words:
                self.logging(
                    f"Lesson {self.current_lesson.title} doesnt have Vocabulary Words",
                    LOGLEVEL.WARN,
                )
            self.current_lesson.lesson_parts.vocab.extend(payload.words)
            self.logging(
                f"Lesson: {self.current_lesson.title} - Sending {len(payload.words)} Vocabulary Words"
            )

            self.task_complete.emit(
                JobRef(
                    id=self.current_lesson.queue_id,
                    task=LESSONTASK.VOCAB,
                    status=JOBSTATUS.COMPLETE,
                ),
                payload,
            )

        else:
            self.logging(
                f"LessonWorker: Error recieving Vocab - {res.status} - {res.message}",
                LOGLEVEL.WARN,
            )
            # TODO handle error
            self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.VOCAB)

        self.on_task_complete(LESSONTASK.VOCAB, True)

    def get_expansion(self):
        self.logging("LessonWorker: Getting Expansion for Lesson")
        self.create_networker(
            "expansion",
            "GET",
            f"{self.host_url}api/v1/lessons/get-expansion?lessonId={self.current_lesson.lesson_id}",
            cb=self.expansion_received,
        )

    def expansion_received(self, res: NetworkResponse):
        self.logging("LessonWorker: Received Expansion Response")
        if res.ok:
            payload = parse_expansion(lesson=self.current_lesson, res_data=res.data)
            if not payload.sentences:
                self.logging(
                    f"Lesson - {self.current_lesson.title} doesnt have a Expansion Section",
                    LOGLEVEL.WARN,
                )
            self.current_lesson.lesson_parts.expansion.extend(payload.sentences)
            self.current_lesson.lesson_parts.all_sentences.extend(payload.sentences)

            self.logging(
                f"Lesson: {self.current_lesson.title} - Sending {len(payload.sentences)} Expansion Sentences"
            )

            self.task_complete.emit(
                JobRef(
                    id=self.current_lesson.queue_id,
                    task=LESSONTASK.EXPANSION,
                    status=JOBSTATUS.COMPLETE,
                ),
                payload,
            )
        else:
            self.logging(
                f"Error recieving Expansion - {res.status} - {res.message} ",
                LOGLEVEL.ERROR,
            )
            self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.EXPANSION)
            # TODO handle error
        self.on_task_complete(LESSONTASK.EXPANSION, True)

    def get_grammar(self):
        self.logging("LessonWorker: Getting Grammar for Lesson")
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
            payload = parse_grammar(lesson=self.current_lesson, res_data=res.data)
            if not payload.sentences:
                self.logging(
                    f"Lesson - {self.current_lesson.title} doesnt have a Grammar Section",
                    LOGLEVEL.WARN,
                )

            self.current_lesson.lesson_parts.all_sentences.extend(payload.sentences)
            self.current_lesson.lesson_parts.grammar.extend(payload.grammar)
            self.logging(
                f"Lesson: {self.current_lesson.title} - Sending {len(payload.sentences)} Grammar Sentences"
            )
            self.task_complete.emit(
                JobRef(
                    id=self.current_lesson.queue_id,
                    task=LESSONTASK.GRAMMAR,
                    status=JOBSTATUS.COMPLETE,
                ),
                payload,
            )
        else:
            self.logging(
                f"LessonWorker: Error recieving Grammar - {res.status} - {res.message}",
                LOGLEVEL.ERROR,
            )
            self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.GRAMMAR)
        self.on_task_complete(LESSONTASK.GRAMMAR, True)
        # self.wait_time(self.wait_time_between_reqs, self.check_lesson_complete)

    def check_lesson_complete(self):
        if self.current_lesson_checked or not self.current_lesson.lesson_id:
            return
        self.current_lesson_checked = True
        self.logging(
            f"Trying to check Complete for Lesson for {self.current_lesson.lesson_id}"
        )
        self.current_lesson.task = LESSONTASK.CHECK
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
