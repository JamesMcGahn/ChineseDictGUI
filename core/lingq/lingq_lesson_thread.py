from PySide6.QtCore import (
    QMutex,
    QMutexLocker,
    QTimer,
    QWaitCondition,
    Signal,
    Slot,
)

from base import QThreadBase
from models.services import JobItem, LingqLessonPayload

from .lingq_lesson_worker import LingqLessonWorker


class LessonLingqLessonThread(QThreadBase):
    task_complete = Signal(object, object)

    def __init__(self, jobs: list[JobItem[LingqLessonPayload]]):
        super().__init__()
        self.jobs = jobs
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._stop = False
        self._paused = False

    @Slot()
    def run(self):
        self.log_thread()

        self.worker = LingqLessonWorker(
            self.jobs,
            self._mutex,
            self._wait_condition,
            self,
        )
        self.worker.moveToThread(self)
        self.worker.finished.connect(self.worker_finished)
        self.worker.task_complete.connect(self.task_complete)
        QTimer.singleShot(0, self.worker.do_work)
        self.exec()

    def worker_finished(self):
        self.worker.deleteLater()
        self.done.emit()

    @Slot()
    def resume(self):
        with QMutexLocker(self._mutex):  # Automatic lock and unlock
            self._paused = False
            self._wait_condition.wakeOne()

    @Slot()
    def pause(self):
        with QMutexLocker(self._mutex):
            self._paused = True

    @Slot()
    def stop(self):
        """Stop the thread."""
        with QMutexLocker(self._mutex):
            self._stop = True
            self._paused = False
            self._wait_condition.wakeAll()
