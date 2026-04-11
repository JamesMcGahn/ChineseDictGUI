from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.network.session import BaseProviderSession

from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QWorkerBase, ThreadCleanUpManager
from keys import keys
from models.services import NetworkResponse
from services.network import NetworkWorker


class CpodNewLoginWorker(QWorkerBase):
    error = Signal()
    cpod_logged_in = Signal(bool)

    def __init__(self, session: BaseProviderSession):
        self.session = session
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
            "https://www.chinesepod.com/login/",
            json={
                "email": keys["email"],
                "passwd": keys["password"],
                "remember": True,
                "clicked": "center",
            },
            retry=1,
            session_provider=self.session,
        )
        networker.moveToThread(net_thread)
        networker.response.connect(self.lingq_login_response)
        net_thread.started.connect(networker.do_work)
        networker.finished.connect(
            lambda: self.clean_up_manager.cleanup_task("cpod-login")
        )
        net_thread.finished.connect(
            lambda: self.clean_up_manager.cleanup_task("cpod-login", True)
        )

        self.clean_up_manager.add_task(
            task_id="cpod-login", thread=net_thread, worker=networker
        )

        net_thread.start()

    def lingq_login_response(self, res: NetworkResponse):
        if res.ok:
            data = res.data
            if "result" in data and data["result"] == "success":
                self.cpod_logged_in.emit(True)
                self.logging("Successfully Logged into Cpod.")
            else:
                self.cpod_logged_in.emit(False)
        else:
            self.logging(f"Error logging to Cpod: {res.status}", "ERROR")
            self.cpod_logged_in.emit(False)
        self.done.emit()
