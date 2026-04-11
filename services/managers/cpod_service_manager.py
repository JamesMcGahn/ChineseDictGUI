from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..network.session import SessionRegistry

from PySide6.QtCore import Signal, Slot

from base import QObjectBase, ThreadQueueManager
from base.enums import EXTRACTDATASOURCE, PROVIDERS
from models.services import CPodLessonPayload, JobRequest

from ..cpod import CpodLessonThread


class CpodServiceManager(QObjectBase):
    appshutdown = Signal()
    task_complete = Signal(object)
    ling_collections = Signal(list)

    def __init__(self, session_registry: SessionRegistry):
        super().__init__()
        self.session_registry = session_registry
        self.queue_manager = ThreadQueueManager("Cpod")

        self.provider_session = self.session_registry.for_provider(PROVIDERS.CPOD)

    @Slot(list)
    def get_lesson_part(
        self,
        job: JobRequest[CPodLessonPayload],
        source: EXTRACTDATASOURCE = EXTRACTDATASOURCE.API,
    ):
        ling_thread = CpodLessonThread(
            job=job, session=self.provider_session, source=source
        )
        ling_thread.task_complete.connect(self.task_complete)
        ling_thread.finished.connect(
            lambda: self.queue_manager.on_finished_thread(ling_thread)
        )
        self.queue_manager.add_thread(ling_thread)
