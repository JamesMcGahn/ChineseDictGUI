from PySide6.QtCore import Qt, Signal

from .qobject_base import QObjectBase
from .qthread_base import QThreadBase


class ThreadQueueManager(QObjectBase):
    thread_running = Signal(bool)

    def __init__(self, thread_type):
        super().__init__()
        self.threads_queue = []
        self.thread_type = thread_type
        self.running = False

    def add_thread(self, thread: QThreadBase):
        thread.done.connect(thread.quit, Qt.QueuedConnection)
        thread.finished.connect(lambda: self.on_finished_thread(thread))
        self.threads_queue.append(thread)
        self.maybe_start_next_thread()

    def on_finished_thread(self, thread: QThreadBase):
        if thread not in self.threads_queue:
            return
        self.running = False
        self.thread_running.emit(self.running)
        self.threads_queue.remove(thread)

        self.logging(f"Removing {self.thread_type} thread {thread} from thread queue")
        thread.deleteLater()

        self.maybe_start_next_thread()

    def maybe_start_next_thread(self):
        if not self.threads_queue:
            return
        if self.running:
            return
        self.running = True
        self.thread_running.emit(self.running)
        head = self.threads_queue[0]
        head.start()
        self.logging(f"Starting {self.thread_type} thread {head}")
