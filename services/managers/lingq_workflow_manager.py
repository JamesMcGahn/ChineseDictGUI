from PySide6.QtCore import QThread, Signal, Slot

from base import QObjectBase, ThreadQueueManager
from core.lingq import LessonLingqLessonThread, LingqCollectionsWorker
from models.services import JobItem, LingqLessonPayload


class LingqWorkFlowManager(QObjectBase):
    appshutdown = Signal()
    task_complete = Signal(object, object)
    ling_collections = Signal(list)

    def __init__(self):
        super().__init__()
        self.queue_manager = ThreadQueueManager("Lingq")

    @Slot(list)
    def create_lingq_lesson(self, jobs: list[JobItem[LingqLessonPayload]]):
        ling_thread = LessonLingqLessonThread(jobs=jobs)
        ling_thread.task_complete.connect(self.task_complete)
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
