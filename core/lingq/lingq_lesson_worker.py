import re
from collections import deque
from random import randint

from PySide6.QtCore import QMutexLocker, QThread, QTimer, Signal, Slot

from base import QWorkerBase, ThreadCleanUpManager
from base.enums import JOBSTATUS
from models.services import JobItem, JobRef, LingqLessonPayload, NetworkResponse
from services.network import NetworkWorker

from .lingq_login_worker import LingqLoginWorker


class LingqLessonWorker(QWorkerBase):
    finished = Signal()
    task_complete = Signal(object, object)

    def __init__(
        self,
        jobs: list[JobItem[LingqLessonPayload]],
        mutex,
        wait_condition,
        parent_thread,
    ):
        super().__init__()
        self._mutex = mutex
        self._wait_condition = wait_condition
        self.parent_thread = parent_thread
        self.lingq_courses = deque(jobs)
        self.running_tasks = {}
        self.clean_up_manager = ThreadCleanUpManager()
        # self.next_page.connect(self.schedule_next)
        self.current_lingq = None
        self.current_lingq_payload = None
        self.current_job_ref = None
        self.current_api_csrf = None
        self.login_attempted = False
        self._busy = False

    @Slot()
    def do_work(self):
        self.log_thread()
        self.get_next_lingq()

    def wait_time(self, range: tuple[int, int], fn):
        random = randint(*range)
        self.logging(
            f"LessonWorker: Waiting {random} secs before sending out next request."
        )
        QTimer.singleShot(random * 1000, fn)

    def get_next_lingq(self):
        if self._busy:
            return
        self._busy = True

        self.current_lingq: JobItem | None = None
        self.current_lingq_payload: LingqLessonPayload | None = None
        self.current_job_ref: JobRef | None = None
        self.current_api_csrf: str | None = None

        if self.lingq_courses:
            with QMutexLocker(self._mutex):
                if self.parent_thread._stop:
                    self._busy = False
                    self.finished.emit()
                    return

                while self.parent_thread._paused:
                    self._wait_condition.wait(self._mutex)

            self.current_lingq = self.lingq_courses.popleft()
            self.current_job_ref, self.current_lingq_payload = self.current_lingq
            self.get_lingq_token()
        else:
            self._busy = False
            self.finished.emit()
            self.logging("Completed Submitted Lingq Lessons", "INFO")

    def get_lingq_token(self):
        net_thread = QThread()
        networker = NetworkWorker(
            "GET",
            "https://www.lingq.com/en/learn/zh/web/editor/",
        )
        task_id = f"{self.current_job_ref.id}-token-{self.current_lingq_payload.title}"
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
                self.wait_time((5, 25), self.lingq_post_lesson)
            else:
                if self.current_lingq:
                    self.lingq_courses.appendleft(self.current_lingq)
                self.wait_time((5, 25), self.login_again)
        else:
            if self.current_lingq:
                self.lingq_courses.appendleft(self.current_lingq)
            self.wait_time((5, 25), self.login_again)

    def login_again(self):
        if self.login_attempted:
            self.login_failure()
            return
        task_id = f"{self.current_job_ref.id}-login"
        login_worker = LingqLoginWorker()
        login_thread = QThread()
        login_worker.moveToThread(login_thread)
        login_worker.lingq_logged_in.connect(self.receive_login)
        login_thread.started.connect(login_worker.do_work)
        self.clean_up_manager.add_task(
            task_id=task_id, thread=login_thread, worker=login_worker
        )
        login_worker.finished.connect(
            lambda: self.clean_up_manager.cleanup_task(task_id)
        )
        login_thread.finished.connect(
            lambda: self.clean_up_manager.cleanup_task(task_id, True)
        )
        login_thread.start()
        self.login_attempted = True

    @Slot(bool)
    def receive_login(self, logged_in: bool):
        if logged_in:
            self.login_attempted = False
            self.wait_time((5, 25), self.get_next_lingq)
        else:
            self.login_failure()

    def login_failure(self):
        self._busy = False
        if self.current_lingq and self.current_lingq not in self.lingq_courses:
            self.lingq_courses.appendleft(self.current_lingq)

        for lingq in self.lingq_courses:
            job_ref, payload = lingq
            self.task_complete.emit(
                JobRef(
                    id=job_ref.id,
                    task=job_ref.task,
                    status=JOBSTATUS.ERROR,
                ),
                {},
            )
        self.finished.emit()

    def lingq_post_lesson(self):
        if self.current_api_csrf is None:
            if self.current_lingq:
                self.lingq_courses.appendleft(self.current_lingq)
            self.wait_time((5, 25), self.login_again)
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
            "title": f"{self.current_lingq_payload.title}",
            "translations": "[]",
            "notes": "",
            "save": "true",
            "collection": self.current_lingq_payload.collection,
        }

        audio_file = open(
            self.current_lingq_payload.audio_file_path,
            "rb",
        )
        text_file = open(
            self.current_lingq_payload.text_file_path,
            "rb",
        )
        files = [
            (
                "audio",
                (
                    self.current_lingq_payload.audio_file_name,
                    audio_file,
                    "audio/mpeg",
                ),
            ),
            (
                "file",
                (
                    self.current_lingq_payload.text_file_name,
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
        )
        networker.moveToThread(net_thread)
        task_id = f"{self.current_job_ref.id}-lingq-{self.current_lingq_payload.title}"
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
        self._busy = False
        if res.ok:
            self.task_complete.emit(
                JobRef(
                    id=self.current_job_ref.id,
                    task=self.current_job_ref.task,
                    status=JOBSTATUS.COMPLETE,
                ),
                {},
            )

        else:
            self.task_complete.emit(
                JobRef(
                    id=self.current_job_ref.id,
                    task=self.current_job_ref.task,
                    status=JOBSTATUS.ERROR,
                ),
                {},
            )
        if self.lingq_courses:
            self.wait_time((15, 30), self.get_next_lingq)
        else:
            self.wait_time((0), self.get_next_lingq)
