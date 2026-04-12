from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.network.session import BaseProviderSession

import uuid
from random import randint

from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QWorkerBase, ThreadCleanUpManager
from base.enums import (
    JOBSTATUS,
    LESSONTASK,
)
from models.services import (
    CPodLessonPayload,
    JobRef,
    JobRequest,
    JobResponse,
    NetworkResponse,
)
from services.network import NetworkWorker


class CpodLessonServiceAPI(QWorkerBase):
    lesson_status = Signal(object)
    task_complete = Signal(object)

    def __init__(
        self,
        job: JobRequest[CPodLessonPayload],
        session: BaseProviderSession,
    ):
        super().__init__()
        self.job = job
        self.session = session
        self.slug = self.job.payload.slug
        self.lesson_id = self.job.payload.lesson_id

        self.token = None
        self.wait_time_between_reqs = (5, 15)
        self.headers = None
        self.clean_up_manager = ThreadCleanUpManager()

        self.handlers = {
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
        self.token = self.session.token
        self.wait_time(
            self.wait_time_between_reqs,
            lambda: self.dispatch(self.job.task),
        )

    def dispatch(self, task: LESSONTASK):
        handler = self.handlers.get(task)
        if not handler:
            raise NotImplementedError
        handler()

    def wait_time(self, range, fn):
        random = randint(*range)
        self.logging(f"Waiting {random} secs before sending out next request.")
        QTimer.singleShot(random * 1000, fn)

    def create_networker(self, task_id, operation, url, json=None):
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
        networker.response.connect(lambda res: self.received_response(res, task_id))
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
        if not self.slug or not self.token:
            self.send_error("CPodLessonPayload missing slug.")
            return

        self.logging(f"Getting Lesson Info for - {self.slug}")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.create_networker(
            "lesson-info",
            "GET",
            url=f"https://www.chinesepod.com/api/v2/lessons/get-lesson?slug={self.slug}",
        )

    def get_dialogue(self):
        self.logging(f"Lesson - {self.slug} - Getting Dialogue")
        if not self.lesson_id:
            self.send_error("CPodLessonPayload missing slug.")
            return
        self.create_networker(
            "dialogue",
            "GET",
            url=f"https://www.chinesepod.com/api/v1/lessons/get-dialogue?lessonId={self.lesson_id}",
        )

    def get_lesson_vocab(self):
        self.logging(f"Lesson - {self.slug} - Getting Vocabulary")
        if not self.lesson_id:
            self.send_error("CPodLessonPayload missing lesson id.")
            return
        self.create_networker(
            "vocab",
            "GET",
            url=f"https://www.chinesepod.com/api/v2/lessons/get-vocab?lessonId={self.lesson_id}",
        )

    def get_expansion(self):
        self.logging(f"Lesson - {self.slug} - Getting Expansion")
        if not self.lesson_id:
            self.send_error("CPodLessonPayload missing lesson id.")
            return
        self.create_networker(
            "expansion",
            "GET",
            f"https://www.chinesepod.com/api/v1/lessons/get-expansion?lessonId={self.lesson_id}",
        )

    def get_grammar(self):
        self.logging(f"Lesson - {self.slug} - Getting Grammar")
        if not self.lesson_id:
            self.send_error("CPodLessonPayload missing lesson id.")
            return
        self.create_networker(
            "grammar",
            "GET",
            f"https://www.chinesepod.com/api/v1/lessons/get-grammar?lessonId={self.lesson_id}",
        )

    def check_lesson_complete(self):
        self.logging(f"Lesson - {self.slug} - Trying to check complete")
        if not self.lesson_id:
            self.send_error("CPodLessonPayload missing lesson id.")
            return
        self.create_networker(
            "toggle-studied",
            "POST",
            url="https://www.chinesepod.com/api/v1/dashboard/toggle-studied",
            json={"lessonId": f"{self.lesson_id}", "status": True},
        )

    def received_response(self, res: NetworkResponse, task_id):
        self.logging(f"Lesson - {self.slug}: Received response for {task_id}")
        self.task_complete.emit(
            JobResponse(
                job_ref=JobRef(
                    id=self.job.id,
                    task=self.job.task,
                    status=(JOBSTATUS.COMPLETE if res.ok else JOBSTATUS.ERROR),
                ),
                payload=res.data,
            )
        )
        self.done.emit()

    def send_error(self, error_msg=None):
        if error_msg:
            self.logging(error_msg, "ERROR")

        self.task_complete.emit(
            JobResponse(
                job_ref=JobRef(
                    id=self.job.id,
                    task=self.job.task,
                    status=(JOBSTATUS.ERROR),
                    error=error_msg,
                ),
                payload=None,
            )
        )
        self.done.emit()
