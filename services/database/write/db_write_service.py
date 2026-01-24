import uuid
from collections import deque

from PySide6.QtCore import QTimer, Signal, Slot

from base import QThreadBase, ThreadCleanUpManager
from base.enums import DBJOBTYPE
from models.services import JobRef
from models.services.database import DBJobPayload

from ..db_manager import DatabaseManager
from .anki_integration_write_service import AnkiIntegrationWriteService
from .base_write_service import BaseWriteService
from .lesson_write_service import LessonWriteService
from .sents_write_service import SentsWriteService
from .words_write_service import WordsWriteService


class DBWriteService(QThreadBase):
    task_complete = Signal(object, object)

    def __init__(self):
        super().__init__()
        self.database_manager = DatabaseManager("chineseDict.db")
        self.database_manager.connect()
        self.write_queue = deque()
        self.running = False
        self.clean_up = ThreadCleanUpManager()
        self.worker_mapping = {
            DBJOBTYPE.LESSONS: LessonWriteService,
            DBJOBTYPE.WORDS: WordsWriteService,
            DBJOBTYPE.SENTENCES: SentsWriteService,
            DBJOBTYPE.ANKI_INTEGRATION: AnkiIntegrationWriteService,
        }

    def run(self):
        self.log_thread()
        QTimer.singleShot(0, self.maybe_start_next_write)
        self.exec()

    @Slot(object, object)
    def add_to_queue(self, job_ref: JobRef, payload: DBJobPayload):
        self.logging(f"Added DB Write Job: {payload.operation.value}")
        self.write_queue.append((job_ref, payload))
        if len(self.write_queue) == 1:
            QTimer.singleShot(0, self.maybe_start_next_write)

    def _build_worker(self, job_ref: JobRef, payload: DBJobPayload) -> BaseWriteService:
        return self.worker_mapping[payload.kind](job_ref, payload)

    def maybe_start_next_write(self):
        if len(self.write_queue) == 0 or self.running:
            return
        self.logging("Starting next DB Write Task.")
        queue_id = uuid.uuid4()
        self.running = True
        jobref, payload = self.write_queue.popleft()
        worker = self._build_worker(jobref, payload)
        task_id = f"{jobref.id}-{payload.operation}-{queue_id}"
        self.clean_up.add_task(task_id, None, worker)
        worker.moveToThread(self)
        worker.setup_db(self.database_manager)
        worker.task_complete.connect(self.task_complete)
        worker.finished.connect(lambda: self.clean_up.cleanup_task(task_id, True))
        worker.finished.connect(self.on_finished)
        QTimer.singleShot(0, worker.do_work)

    def on_finished(self):
        self.running = False
        QTimer.singleShot(0, self.maybe_start_next_write)
