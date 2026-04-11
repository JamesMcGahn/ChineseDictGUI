from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.network.session import BaseProviderSession

from PySide6.QtCore import (
    QTimer,
    Signal,
    Slot,
)

from base import QThreadBase

# from .cpod_lesson_service_scrape import CpodLessonServiceScrape
from base.enums import EXTRACTDATASOURCE
from models.services import CPodLessonPayload, JobRequest

from .cpod_lesson_service_api import CpodLessonServiceAPI


class CpodLessonThread(QThreadBase):
    task_complete = Signal(object)

    def __init__(
        self,
        job: JobRequest[CPodLessonPayload],
        session: BaseProviderSession,
        source: EXTRACTDATASOURCE = EXTRACTDATASOURCE.API,
    ):
        super().__init__()

        self.job = job
        self.session = session
        self.source = source

    @Slot()
    def run(self):
        self.log_thread()
        if self.source == EXTRACTDATASOURCE.API:
            self.worker = CpodLessonServiceAPI(self.job, self.session)
        # else:
        #     self.worker = CpodLessonServiceScrape(self.job, self.session)
        self.worker.moveToThread(self)
        self.worker.done.connect(self.worker_finished)
        self.worker.task_complete.connect(self.task_complete)
        QTimer.singleShot(0, self.worker.do_work)
        self.exec()

    def worker_finished(self):
        self.worker.deleteLater()
        self.done.emit()
