import re

from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QWorkerBase, ThreadCleanUpManager
from keys import keys
from models.services import NetworkResponse
from services.network import NetworkWorker


class LingqLoginWorker(QWorkerBase):
    error = Signal()
    lingq_logged_in = Signal(bool)

    def __init__(self):
        super().__init__()
        self.clean_up_manager = ThreadCleanUpManager()

    @Slot()
    def do_work(self):
        self.log_thread()
        QTimer.singleShot(0, self.lingq_login)

    def lingq_login(self):
        net_thread = QThread()
        networker = NetworkWorker(
            "POST",
            "https://www.lingq.com/en/accounts/login/",
            data={
                "username": keys["email"],
                "password": keys["lingqpw"],
                "remember-me": "on",
            },
        )
        networker.moveToThread(net_thread)
        networker.response.connect(self.lingq_login_response)
        net_thread.started.connect(networker.do_work)
        networker.finished.connect(
            lambda: self.clean_up_manager.cleanup_task("lingq-login")
        )
        net_thread.finished.connect(
            lambda: self.clean_up_manager.cleanup_task("lingq-login", True)
        )

        self.clean_up_manager.add_task(
            task_id="lingq-login", thread=net_thread, worker=networker
        )

        net_thread.start()

    def lingq_login_response(self, res: NetworkResponse):
        if res.ok:
            data = res.data
            match = re.search(r"csrfToken:\s*'([^']+)'", data)
            if match:
                self.lingq_logged_in.emit(True)
                self.logging("Successfully Logged into Lingq.")
            else:
                self.lingq_logged_in.emit(False)
        else:
            self.logging(f"Error logging to Lingq: {res.status}", "ERROR")
            self.lingq_logged_in.emit(False)
        self.finished.emit()
