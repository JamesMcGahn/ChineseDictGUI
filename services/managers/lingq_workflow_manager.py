from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..network.session import SessionRegistry

from PySide6.QtCore import QThread, Signal, Slot

from base import QObjectBase, ThreadQueueManager
from base.enums import PROVIDERS
from core.lingq import LessonLingqLessonThread, LingqCollectionsWorker
from models.services import JobRequest, LingqLessonPayload


class LingqWorkFlowManager(QObjectBase):
    appshutdown = Signal()
    task_complete = Signal(object)
    ling_collections = Signal(list)

    def __init__(self, session_registry: SessionRegistry):
        super().__init__()
        self.session_registry = session_registry
        self.queue_manager = ThreadQueueManager("Lingq")

        self.provider_session = self.session_registry.for_provider(PROVIDERS.LINGQ)

    @Slot(list)
    def create_lingq_lesson(self, jobs: list[JobRequest[LingqLessonPayload]]):
        ling_thread = LessonLingqLessonThread(jobs=jobs, session=self.provider_session)
        ling_thread.task_complete.connect(self.task_complete)
        ling_thread.finished.connect(
            lambda: self.queue_manager.on_finished_thread(ling_thread)
        )
        self.queue_manager.add_thread(ling_thread)

    @Slot()
    def get_current_lingq_collections(self):
        self.lingcollect_thread = QThread()
        self.lingcollect = LingqCollectionsWorker()
        self.lingcollect.moveToThread(self.lingcollect_thread)
        self.lingcollect_thread.started.connect(self.lingcollect.do_work)
        self.lingcollect.lingq_categories.connect(self.received_lingq_collections)
        self.lingcollect.finished.connect(self.lingcollect_thread.quit)
        self.lingcollect_thread.finished.connect(self.lingcollect_thread.deleteLater)
        self.lingcollect_thread.start()

    def received_lingq_collections(self, collections: list):
        self.collections = collections
        self.ling_collections.emit(collections)
