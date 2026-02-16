from PySide6.QtCore import QObject, Slot


class ThreadCleanUpManager(QObject):

    def __init__(self):
        super().__init__()
        self.running_tasks = {}

    @Slot(str, bool)
    def cleanup_task(self, task_id, thread_finished=False):
        if task_id not in self.running_tasks:
            return

        w_thread, worker = self.running_tasks[task_id]

        if not thread_finished:
            if w_thread and w_thread.isRunning():
                print(f"Task {task_id} - Thread Quitting.")
                w_thread.quit()
            return

        w_thread, worker = self.running_tasks.pop(task_id)
        print(f"Task {task_id} - Thread & Worker Deleting.")
        if worker:
            worker.deleteLater()

        if w_thread:
            w_thread.deleteLater()

    def add_task(self, task_id, thread, worker):
        self.running_tasks[task_id] = (thread, worker)
        print(self.running_tasks)
