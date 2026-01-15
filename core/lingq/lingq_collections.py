import uuid

from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QWorkerBase, ThreadCleanUpManager
from keys import keys
from models.services import NetworkResponse
from services.network import NetworkWorker


class LingqCollectionsWorker(QWorkerBase):
    finished = Signal()
    lingq_categories = Signal(list)
    next_page = Signal()
    error = Signal(int)

    def __init__(self):
        super().__init__()
        self.lingq_courses = []
        self.page = 1
        self.next_page.connect(self.schedule_next)
        self.clean_up_manager = ThreadCleanUpManager()

    @Slot()
    def do_work(self):
        self.log_thread()
        QTimer.singleShot(0, self.get_lingq_courses)

    def get_lingq_courses(self):
        self.logging("LinqgCollectionsWorker: Getting Lingq Courses")
        net_thread = QThread()
        networker = NetworkWorker(
            "GET",
            f"https://www.lingq.com/api/v3/zh/collections/my/?page={self.page}&page_size=25&search_criteria=contains&sort=recentUsed&username={keys["lingqusername"]}",
        )
        networker.moveToThread(net_thread)
        networker.response.connect(self.lingq_courses_response)
        task_id = f"collections-{self.page}-{uuid.uuid4()}"
        net_thread.started.connect(networker.do_work)
        networker.finished.connect(lambda: self.clean_up_manager.cleanup_task(task_id))
        net_thread.finished.connect(
            lambda: self.clean_up_manager.cleanup_task(task_id, True)
        )

        self.clean_up_manager.add_task(
            task_id=task_id, thread=net_thread, worker=networker
        )

        net_thread.start()

    def lingq_courses_response(self, res: NetworkResponse):
        self.logging("LinqgCollectionsWorker: Received Response Lingq Courses")
        if res.ok:
            result = res.data

            if "results" in result and len(result["results"]) > 0:
                self.lingq_courses.extend(result["results"])
                self.logging(
                    f"LinqgCollectionsWorker: Received Page: {self.page} of Lingq Courses"
                )
                print(result)
            if "next" in result and result["next"] is not None:

                self.page += 1
                self.logging(
                    f"LinqgCollectionsWorker: Trying to Get Page {self.page} of Ling Courses"
                )
                self.next_page.emit()
            else:
                self.logging(
                    f"LinqgCollectionsWorker: Received all  {len(self.lingq_courses)} Lingq Courses"
                )
                self.lingq_categories.emit(self.lingq_courses)
                self.finished.emit()
        else:
            self.logging(f"Error receiving Lingq Course: {res.status}", "ERROR")
            self.lingq_categories.emit(self.lingq_courses)
            self.finished.emit()

    @Slot(int)
    def schedule_next(self):
        self.wait_time(15, self.get_lingq_courses)
