import uuid
from collections import deque
from random import randint

from PySide6.QtCore import QMutexLocker, QThread, QTimer, Signal, Slot

from base import QWorkerBase, ThreadCleanUpManager
from base.enums import (
    JOBSTATUS,
    LESSONSTATUS,
    LESSONTASK,
    LOGLEVEL,
)
from keys import keys
from models.core import LessonTaskPayload
from models.dictionary import Lesson
from models.services import (
    CPodLessonPayload,
    JobRef,
    JobRequest,
    JobResponse,
    NetworkResponse,
)
from services.network import NetworkWorker
from services.network.session import BaseProviderSession

from .lesson_parsers import (
    extract_slug,
    parse_dialogue,
    parse_expansion,
    parse_grammar,
    parse_lesson_info,
    parse_vocab,
)


class LessonScraperWorkerV2(QWorkerBase):
    lesson_status = Signal(object)
    task_complete = Signal(object)

    def __init__(
        self,
        lesson_list: list[JobRequest[CPodLessonPayload]],
        mutex,
        wait_condition,
        parent_thread,
        session: BaseProviderSession,
    ):
        super().__init__()
        self.lesson_list = deque(lesson_list)
        self._mutex = mutex
        self._wait_condition = wait_condition
        self.parent_thread = parent_thread
        self.session = session
        self.host_url = keys["url"]

        self.token = None
        self.wait_time_between_reqs = (5, 15)

        self.current_lesson: Lesson | None = None
        self.completed_lessons = []
        self.errored_lessons = []

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

        self.error_task_map = {
            LESSONTASK.INFO: self.lesson_failed,
            LESSONTASK.DIALOGUE: self.lesson_failed,
            LESSONTASK.VOCAB: self.get_expansion,
            LESSONTASK.EXPANSION: self.get_grammar,
            LESSONTASK.GRAMMAR: self.check_lesson_complete,
        }

    @Slot()
    def do_work(self):
        self.log_thread()
        self.get_next_lesson()

    def wait_time(self, range, fn):
        random = randint(*range)
        self.logging(f"Waiting {random} secs before sending out next request.")
        QTimer.singleShot(random * 1000, fn)

    def send_status_update(self, status: LESSONSTATUS, task: LESSONTASK):
        self.lesson_status.emit(
            {
                "queue_id": self.current_lesson.queue_id,
                "status": status,
                "task": task,
            }
        )

    def send_task_complete_payload(
        self, task: LESSONTASK, payload: LessonTaskPayload, error=False
    ):

        if payload is None:
            payload = LessonTaskPayload(success=not error)

        self.task_complete.emit(
            JobResponse(
                job_ref=JobRef(
                    id=self.current_lesson.queue_id,
                    task=task,
                    status=(JOBSTATUS.COMPLETE if not error else JOBSTATUS.ERROR),
                ),
                payload=payload,
            )
        )

    def get_next_lesson(self):
        self.current_lesson = None
        self.current_lesson_checked = False
        self.token = self.session.token
        self.logging(f"Total Lessons to Scrape: {len(self.lesson_list)} Lessons")

        self.headers = {"Authorization": f"Bearer {self.token}"}

        if self.lesson_list:
            with QMutexLocker(self._mutex):
                if self.parent_thread._stop:
                    self.done.emit()

                while self.parent_thread._paused:
                    self._wait_condition.wait(self._mutex)

            spec = self.lesson_list.popleft()

            if not self.token:
                self.logging("No Token found", "ERROR")
                self.lesson_completed(error=True)
                return

            self.current_lesson = Lesson(
                provider="cpod",
                url=spec.payload.url,
                queue_id=spec.id,
                slug=spec.payload.url,
            )

            self.send_status_update(LESSONSTATUS.IN_PROGRESS, LESSONTASK.INFO)
            self.logging(f"Trying to scrape {self.current_lesson.url}")

            slug = extract_slug(self.current_lesson.url)

            if slug is None:
                self.logging("Lesson does not have a correct URL", LOGLEVEL.ERROR)
                self.send_status_update(LESSONSTATUS.ERROR, LESSONTASK.INFO)
                self.lesson_completed(error=True)
                return

            self.current_lesson.slug = slug

            self.wait_time(
                self.wait_time_between_reqs,
                lambda: self.dispatch(LESSONTASK.INFO),
            )

        else:
            self.logging(
                f"Finished getting all lessons. Completed: {len(self.completed_lessons)} Errored: {len(self.errored_lessons)} "
            )
            self.done.emit()

    def dispatch(self, task: LESSONTASK, error=False):
        self.send_status_update(LESSONSTATUS.IN_PROGRESS, task)
        if error:
            handler = self.error_task_map[task]
        else:
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

    def on_task_complete(self, task: LESSONTASK, success=True):
        if not success:
            self.logging(f"Task {task} failed", LOGLEVEL.ERROR)
            self.send_status_update(LESSONSTATUS.ERROR, task)
            self.send_task_complete_payload(task=task, payload=None, error=True)
            self.wait_time(
                self.wait_time_between_reqs, lambda: self.dispatch(task, error=True)
            )
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
            session_provider=self.session,
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
        self.logging(f"Getting Lesson Info for - {slug}")

        self.create_networker(
            "lesson-info",
            "GET",
            url=f"{self.host_url}api/v2/lessons/get-lesson?slug={slug}",
            cb=self.lesson_info_received,
        )

    def lesson_info_received(self, res: NetworkResponse):
        self.logging("Recieved Response for Lesson Info")
        if res.ok:
            payload = parse_lesson_info(res.data)
            if payload.lesson_info is None:
                self.on_task_complete(LESSONTASK.INFO, False)
                return
            self.current_lesson.hash_code = payload.lesson_info.hash_code
            self.current_lesson.level = payload.lesson_info.level
            self.current_lesson.lesson_id = payload.lesson_info.lesson_id
            self.current_lesson.title = payload.lesson_info.title
            self.send_task_complete_payload(task=LESSONTASK.INFO, payload=payload)
            self.on_task_complete(LESSONTASK.INFO, True)
        else:
            self.logging(
                "Did not receive the Lesson Information. Skipping Lesson",
                LOGLEVEL.ERROR,
            )
            self.on_task_complete(LESSONTASK.INFO, False)

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
        self.logging("Received Response for Dialog")
        if res.ok:
            payload = parse_dialogue(lesson=self.current_lesson, res_data=res.data)

            if not payload.sentences:
                self.logging(
                    f"Lesson - {self.current_lesson.title}  doesnt have a Dialogue Section",
                    LOGLEVEL.WARN,
                )

            self.logging(
                f"Lesson: {self.current_lesson.title} - Sending {len(payload.sentences)} Dialogue Sentences"
            )
            self.send_task_complete_payload(task=LESSONTASK.DIALOGUE, payload=payload)
            self.on_task_complete(LESSONTASK.DIALOGUE, True)
        else:
            self.logging(
                f"Error receiving Dialogue - {res.status} -{res.message}",
                LOGLEVEL.WARN,
            )
            self.on_task_complete(LESSONTASK.DIALOGUE, False)

    def get_lesson_vocab(self):
        self.logging("Getting Vocabulary for Lesson")
        self.create_networker(
            "vocab",
            "GET",
            url=f"{self.host_url}api/v2/lessons/get-vocab?lessonId={self.current_lesson.lesson_id}",
            cb=self.vocab_received,
        )

    def vocab_received(self, res: NetworkResponse):
        self.logging("Received Vocab Response for Lesson")
        if res.ok:
            payload = parse_vocab(lesson=self.current_lesson, res_data=res.data)

            if not payload.words:
                self.logging(
                    f"Lesson {self.current_lesson.title} doesnt have Vocabulary Words",
                    LOGLEVEL.WARN,
                )

            self.logging(
                f"Lesson: {self.current_lesson.title} - Sending {len(payload.words)} Vocabulary Words"
            )

            self.send_task_complete_payload(task=LESSONTASK.VOCAB, payload=payload)
            self.on_task_complete(LESSONTASK.VOCAB, True)
        else:
            self.logging(
                f"Error recieving Vocab - {res.status} - {res.message}",
                LOGLEVEL.WARN,
            )
            self.on_task_complete(LESSONTASK.VOCAB, False)

    def get_expansion(self):
        self.logging("Getting Expansion for Lesson")
        self.create_networker(
            "expansion",
            "GET",
            f"{self.host_url}api/v1/lessons/get-expansion?lessonId={self.current_lesson.lesson_id}",
            cb=self.expansion_received,
        )

    def expansion_received(self, res: NetworkResponse):
        self.logging("Received Expansion Response")
        if res.ok:
            payload = parse_expansion(lesson=self.current_lesson, res_data=res.data)
            if not payload.sentences:
                self.logging(
                    f"Lesson - {self.current_lesson.title} doesnt have a Expansion Section",
                    LOGLEVEL.WARN,
                )

            self.logging(
                f"Lesson: {self.current_lesson.title} - Sending {len(payload.sentences)} Expansion Sentences"
            )

            self.send_task_complete_payload(task=LESSONTASK.EXPANSION, payload=payload)
            self.on_task_complete(LESSONTASK.EXPANSION, True)
        else:
            self.logging(
                f"Error recieving Expansion - {res.status} - {res.message} ",
                LOGLEVEL.ERROR,
            )
            self.on_task_complete(LESSONTASK.EXPANSION, False)

    def get_grammar(self):
        self.logging("Getting Grammar for Lesson")
        self.create_networker(
            "grammar",
            "GET",
            f"{self.host_url}api/v1/lessons/get-grammar?lessonId={self.current_lesson.lesson_id}",
            cb=self.grammar_received,
        )

    def grammar_received(self, res: NetworkResponse):
        self.logging("Received Grammar Response for Lesson")
        if res.ok:
            payload = parse_grammar(lesson=self.current_lesson, res_data=res.data)
            if not payload.success:
                self.on_task_complete(LESSONTASK.GRAMMAR, False)

            if not payload.sentences:
                self.logging(
                    f"Lesson - {self.current_lesson.title} doesnt have a Grammar Section",
                    LOGLEVEL.WARN,
                )

            self.logging(
                f"Lesson: {self.current_lesson.title} - Sending {len(payload.sentences)} Grammar Sentences"
            )

            self.send_task_complete_payload(task=LESSONTASK.GRAMMAR, payload=payload)
            self.on_task_complete(LESSONTASK.GRAMMAR, True)
        else:
            self.logging(
                f"Error recieving Grammar - {res.status} - {res.message}",
                LOGLEVEL.ERROR,
            )
            self.on_task_complete(LESSONTASK.GRAMMAR, False)

    def check_lesson_complete(self):
        if self.current_lesson_checked or not self.current_lesson.lesson_id:
            return
        self.current_lesson_checked = True
        self.logging(
            f"Trying to check Complete for Lesson for {self.current_lesson.lesson_id}"
        )
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

        self.send_status_update(LESSONSTATUS.COMPLETE, LESSONTASK.CHECK)
        self.send_task_complete_payload(task=LESSONTASK.CHECK, payload=None)
        QTimer.singleShot(1000, self.lesson_completed)

    def lesson_failed(self):
        self.lesson_completed(True)

    def lesson_completed(self, error=False):
        if error:
            self.errored_lessons.append(self.current_lesson)
        else:
            if not self.current_lesson_checked:
                self.check_lesson_complete()
                return
            else:
                self.logging(f"Completed Lesson - {self.current_lesson.title}")
                self.completed_lessons.append(self.current_lesson)

        wait_time = randint(10, 90) if self.lesson_list else 0
        self.logging(f"Waiting {wait_time} seconds before scraping next lesson.")
        QTimer.singleShot(wait_time * 1000, self.get_next_lesson)
