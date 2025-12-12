from PySide6.QtCore import QMetaObject, QObject


class CleanUpManager(QObject):

    def __init__(self):
        super().__init__(self)

        self.running_tasks = {}

    def cleanup_task(self, task_id, thread_finished=False):
        if task_id in self.running_tasks:
            if thread_finished:
                w_thread, worker = self.running_tasks.pop(task_id)
                w_thread.deleteLater()
                print(f"Task {task_id} - Thread deleting.")
            else:
                w_thread, worker = self.running_tasks[task_id]
                if worker:
                    worker.deleteLater()
                w_thread.quit()
                print(f"Task {task_id} - Worker cleaned up. Thread quitting.")
