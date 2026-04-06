from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.network import ProviderSession

import re
from collections import deque
from random import randint

from PySide6.QtCore import QMutexLocker, QThread, QTimer, Signal, Slot

from base import QWorkerBase, ThreadCleanUpManager
from base.enums import JOBSTATUS
from models.services import (
    JobRef,
    JobRequest,
    JobResponse,
    LingqLessonPayload,
    NetworkResponse,
)
from services.network import NetworkWorker

from .lingq_login_worker import LingqLoginWorker


class LingqLessonWorker(QWorkerBase):
    task_complete = Signal(object)

    def __init__(
        self,
        jobs: list[JobRequest[LingqLessonPayload]],
        mutex,
        wait_condition,
        parent_thread,
        session: ProviderSession,
    ):
        super().__init__()
        self._mutex = mutex
        self._wait_condition = wait_condition
        self.parent_thread = parent_thread
        self.lingq_courses = deque(jobs)
        self.running_tasks = {}
        self.clean_up_manager = ThreadCleanUpManager()
        self.session = session

        self.current_lingq = None

        self.current_api_csrf = None
        self.login_attempted = False
        self._busy = False

        self.wait_range_between_steps = (25, 90)
        self.wait_range_between_submissions = (25, 120)

    @Slot()
    def do_work(self):
        self.log_thread()
        self.wait_time(self.wait_range_between_steps, self.get_next_lingq)

    def wait_time(self, range: tuple[int, int], fn):
        random = randint(*range)
        self.logging(f"Waiting {random} secs before sending out next request.")
        QTimer.singleShot(random * 1000, fn)

    def get_next_lingq(self):
        if self._busy:
            return
        self._busy = True

        self.current_lingq = None
        self.current_api_csrf = None

        self.logging(f"Total Lessons to Submit: {len(self.lingq_courses)} Lessons")
        if self.lingq_courses:
            with QMutexLocker(self._mutex):
                if self.parent_thread._stop:
                    self._busy = False
                    self.send_error_all("Stopped by User")
                    self.done.emit()
                    return

                while self.parent_thread._paused:
                    self._wait_condition.wait(self._mutex)

            self.current_lingq = self.lingq_courses.popleft()

            self.get_lingq_token()
        else:
            self._busy = False
            self.done.emit()
            self.logging("Completed Submitted Lingq Lessons", "INFO")

    def get_lingq_token(self):
        self._busy = True
        self.logging(f"Getting Lesson Token for - {self.current_lingq.payload.title}")
        net_thread = QThread()
        networker = NetworkWorker(
            "GET",
            "https://www.lingq.com/en/learn/zh/web/editor/",
            retry=1,
            session_provider=self.session,
        )
        task_id = f"{self.current_lingq.id}-token-{self.current_lingq.payload.title}"
        networker.moveToThread(net_thread)
        networker.response.connect(self.lingq_token_response)
        net_thread.started.connect(networker.do_work)
        self.clean_up_manager.add_task(
            task_id=task_id, thread=net_thread, worker=networker
        )
        networker.finished.connect(lambda: self.clean_up_manager.cleanup_task(task_id))
        net_thread.finished.connect(
            lambda: self.clean_up_manager.cleanup_task(task_id, True)
        )
        net_thread.start()

    def lingq_token_response(self, res: NetworkResponse):
        self._busy = False
        self.logging(f"Received Lesson Token for - {self.current_lingq.payload.title}")
        if res.ok:
            data = res.data
            match = re.search(r"csrfToken:\s*'([^']+)'", data)
            if not match:
                self.logging("Failed to extract CSRF token", "ERROR")
            api_csrf = None
            if match:
                api_csrf = match.group(1)
            if api_csrf:
                self.current_api_csrf = api_csrf
                self.wait_time(self.wait_range_between_steps, self.lingq_post_lesson)
                self.logging(
                    f"Found Lesson Token for - {self.current_lingq.payload.title}"
                )
            else:
                if self.current_lingq:
                    self.logging(
                        f"Failed to Get Lesson Token for - {self.current_lingq.payload.title}"
                    )
                    self.lingq_courses.appendleft(self.current_lingq)
                self.wait_time(self.wait_range_between_submissions, self.login_again)
        else:
            if self.current_lingq:
                self.lingq_courses.appendleft(self.current_lingq)
                self.logging(
                    f"Failed to Get Lesson Token for - {self.current_lingq.payload.title}"
                )
            self.wait_time(self.wait_range_between_submissions, self.login_again)

    def login_again(self):
        self._busy = True
        self.logging("Attempting to Login Again", "WARN")
        if self.login_attempted:
            self.logging("Login already attempted. Not trying again", "WARN")
            self.login_failure()
            return
        task_id = f"{self.current_lingq.id}-login"
        login_worker = LingqLoginWorker(session=self.session)
        login_thread = QThread()
        login_worker.moveToThread(login_thread)
        login_worker.lingq_logged_in.connect(self.receive_login)
        login_thread.started.connect(login_worker.do_work)
        self.clean_up_manager.add_task(
            task_id=task_id, thread=login_thread, worker=login_worker
        )
        login_worker.done.connect(lambda: self.clean_up_manager.cleanup_task(task_id))
        login_thread.finished.connect(
            lambda: self.clean_up_manager.cleanup_task(task_id, True)
        )
        login_thread.start()
        self.login_attempted = True

    @Slot(bool)
    def receive_login(self, logged_in: bool):
        self._busy = False
        if logged_in:
            self.login_attempted = False
            self.logging("Log in Succeed. Reattempting Ling Submission", "WARN")

            self.wait_time(self.wait_range_between_submissions, self.get_next_lingq)
        else:
            self.logging("Login Failed. Reattempting Log in", "WARN")
            self.wait_time((0, 1), self.login_failure)

    def login_failure(self):
        self._busy = False
        self.logging("Failed to log in to Lingq", "ERROR")
        self.send_error_all("Failed to log in to Lingq")
        self.done.emit()

    def lingq_post_lesson(self):
        self._busy = True
        self.logging(
            f"Attempting to Submit Lesson - {self.current_lingq.payload.title}",
            "INFO",
        )
        if self.current_api_csrf is None:
            if self.current_lingq:
                self.lingq_courses.appendleft(self.current_lingq)
                self.logging(
                    "No Token for Submission. Trying log in Again",
                    "INFO",
                )
            self.wait_time((20, 60), self.login_again)
            return

        net_thread = QThread()
        payload = {
            "description": "",
            "hasPrice": "false",
            "isProtected": "false",
            "isHiddden": "true",
            "language": "zh",
            "status": "private",
            "tags": "",
            "title": f"{self.current_lingq.payload.title}",
            "translations": "[]",
            "notes": "",
            "save": "true",
            "collection": self.current_lingq.payload.collection,
        }

        audio_file = open(
            self.current_lingq.payload.audio_file_path,
            "rb",
        )
        text_file = open(
            self.current_lingq.payload.text_file_path,
            "rb",
        )
        files = [
            (
                "audio",
                (
                    self.current_lingq.payload.audio_file_name,
                    audio_file,
                    "audio/mpeg",
                ),
            ),
            (
                "file",
                (
                    self.current_lingq.payload.text_file_name,
                    text_file,
                    "text/plain",
                ),
            ),
        ]
        headers = {"http_x_csrftoken": self.current_api_csrf}
        networker = NetworkWorker(
            "POST",
            "https://www.lingq.com/api/v3/zh/lessons/import/",
            headers=headers,
            files=files,
            data=payload,
            retry=1,
            session_provider=self.session,
        )
        networker.moveToThread(net_thread)
        task_id = f"{self.current_lingq.id}-lingq-{self.current_lingq.payload.title}"
        networker.response.connect(self.lesson_post_response)
        net_thread.started.connect(networker.do_work)
        networker.finished.connect(
            lambda: self.clean_up_manager.cleanup_task(task_id=task_id)
        )
        net_thread.finished.connect(
            lambda: self.clean_up_manager.cleanup_task(
                task_id=task_id,
                thread_finished=True,
            )
        )
        net_thread.finished.connect(audio_file.close)
        net_thread.finished.connect(text_file.close)
        self.clean_up_manager.add_task(
            task_id=task_id, thread=net_thread, worker=networker
        )
        net_thread.start()

    def lesson_post_response(self, res: NetworkResponse):
        self.logging(
            "Received Response for Lingq Lesson Submission",
            "INFO",
        )
        self._busy = False
        if res.ok:
            self.task_complete.emit(
                JobResponse(
                    job_ref=JobRef(
                        id=self.current_lingq.id,
                        task=self.current_lingq.task,
                        status=JOBSTATUS.COMPLETE,
                    ),
                    payload=None,
                )
            )
            self.logging(
                f"Submission Succeeded for - {self.current_lingq.payload.title}",
                "INFO",
            )
        else:
            self.logging(
                f"Submission Failed for - {self.current_lingq.payload.title}",
                "ERROR",
            )
            self.task_complete.emit(
                JobResponse(
                    job_ref=JobRef(
                        id=self.current_lingq.id,
                        task=self.current_lingq.task,
                        status=JOBSTATUS.ERROR,
                    ),
                    payload=None,
                )
            )

        self.logging(
            "Attempting to Get Next Lesson for Submission",
            "INFO",
        )
        if self.lingq_courses:
            self.wait_time(self.wait_range_between_submissions, self.get_next_lingq)
        else:
            self.wait_time((0, 1), self.get_next_lingq)

    def send_error_all(self, error_message):
        if self.current_lingq and self.current_lingq not in self.lingq_courses:
            self.lingq_courses.appendleft(self.current_lingq)

        for lingq in self.lingq_courses:
            self.task_complete.emit(
                JobResponse(
                    job_ref=JobRef(
                        id=lingq.id,
                        task=lingq.task,
                        status=JOBSTATUS.ERROR,
                        error=error_message,
                    ),
                    payload=None,
                )
            )
