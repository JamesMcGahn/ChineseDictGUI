import time

from PySide6.QtCore import Signal, Slot

from base import QObjectBase, ThreadQueueManager

from ..database.read import DBReadService

# TODO update db code when context db thread is built out


class DatabaseServiceManager(QObjectBase):
    appshutdown = Signal()
    task_complete = Signal(object, object)
    pagination = Signal(object, int, int, int, bool, bool)
    result = Signal(list)

    def __init__(self):
        super().__init__()
        self.read_service = DBReadService()
        self.read_service.result.connect(self.result)
        self.read_service.pagination.connect(self.pagination)

    @property
    def read(self) -> DBReadService:
        return self.read_service

    def write(self, jobref, payload):
        pass
