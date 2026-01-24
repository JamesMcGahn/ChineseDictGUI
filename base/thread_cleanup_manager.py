from PySide6.QtCore import QObject, Slot


class ThreadCleanUpManager(QObject):

    def __init__(self):
        super().__init__()
        self.running_tasks = {}

    @Slot(str, bool)
    def cleanup_task(self, task_id, thread_finished=False):
        if task_id in self.running_tasks:
            if thread_finished:
                w_thread, worker = self.running_tasks.pop(task_id)
                if w_thread:
                    w_thread.deleteLater()
                if worker:
                    worker.deleteLater()
                print(f"Task {task_id} - Thread & Worker Deleting.")
            else:
                w_thread, worker = self.running_tasks[task_id]
                w_thread.quit()
                print(f"Task {task_id} - Thread Quitting.")

    def add_task(self, task_id, thread, worker):
        self.running_tasks[task_id] = (thread, worker)
        print(self.running_tasks)
