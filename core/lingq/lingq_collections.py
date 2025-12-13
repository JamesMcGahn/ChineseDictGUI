from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QWorkerBase
from keys import keys
from services.network import NetworkWorker


class LingqCollectionsWorker(QWorkerBase):
    finished = Signal()
    lingq_categories = Signal(list)
    next_page = Signal(int)
    error = Signal(int)

    def __init__(self):
        super().__init__()
        self.networkers = []
        self.lingq_courses = []
        self.running_tasks = {}
        self.next_page.connect(self.schedule_next)

    @Slot()
    def do_work(self):
        self.log_thread()
        QTimer.singleShot(10 * 1000, lambda: self.get_lingq_courses(page=1))

    def get_lingq_courses(self, page=1):
        net_thread = QThread()
        networker = NetworkWorker(
            "GET",
            f"https://www.lingq.com/api/v3/zh/collections/my/?page={page}&page_size=25&search_criteria=contains&sort=recentUsed&username={keys["lingqusername"]}",
        )
        networker.moveToThread(net_thread)
        networker.response.connect(
            lambda res: self.lingq_courses_response(res, page + 1)
        )
        net_thread.started.connect(networker.do_work)
        networker.finished.connect(lambda: self.cleanup_task(f"page-{page}"))
        net_thread.finished.connect(lambda: self.cleanup_task(f"page-{page}", True))
        self.running_tasks[f"page-{page}"] = (net_thread, networker)
        net_thread.start()

    def lingq_courses_response(self, response, page):
        if response["ok"]:
            result = response["data"]

            if "results" in result and len(result["results"]) > 0:
                self.lingq_courses.extend(result["results"])
                self.logging(f"Received Page: {page -1} of Lingq Courses")

            if "next" in result and result["next"] is not None:
                self.next_page.emit(page)
            else:
                self.lingq_categories.emit(self.lingq_courses)
                self.finished.emit()
        else:
            self.logging(f"Error receiving Lingq Course: {response["status"]}", "ERROR")
            self.error.emit(response["status"])
            self.finished.emit()

    @Slot(int)
    def schedule_next(self, page):
        self.wait_time(10, lambda: self.get_lingq_courses(page))

    def cleanup_task(self, task_id, thread_finished=False):
        if task_id in self.running_tasks:
            if thread_finished:
                w_thread, worker = self.running_tasks.pop(task_id)
                w_thread.deleteLater()
                self.logging(
                    f"LingqCollectionsWorker: Task {task_id} - Thread deleting."
                )
            else:
                w_thread, worker = self.running_tasks[task_id]
                if worker:
                    worker.deleteLater()
                w_thread.quit()
                self.logging(
                    f"LingqCollectionsWorker: Task {task_id} - Worker cleaned up. Thread quitting."
                )
