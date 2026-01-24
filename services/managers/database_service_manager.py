from typing import Any

from PySide6.QtCore import Signal, Slot

from base import QObjectBase
from models.services import JobRef
from models.services.database import DBJobPayload

from ..database import DatabaseManager
from ..database.read import DBReadService
from ..database.write.db_write_service import DBWriteService


class DatabaseServiceManager(QObjectBase):
    appshutdown = Signal()
    task_complete = Signal(object, object)
    add_to_write_queue = Signal(object, object)

    def __init__(self):
        super().__init__()
        self._setup_database()
        self.read_service = DBReadService()
        self.write_service = DBWriteService()
        self.write_service.task_complete.connect(self.task_complete)
        self.add_to_write_queue.connect(self.write_service.add_to_queue)
        self.write_service.finished.connect(self.write_service.deleteLater)
        self.write_service.start()
        self.appshutdown.connect(self.shut_down_write_service)

    @property
    def read(self) -> DBReadService:
        return self.read_service

    @Slot(object, object)
    def write(self, job_ref: JobRef, payload: DBJobPayload[Any]):
        self.add_to_write_queue.emit(job_ref, payload)

    def shut_down_write_service(self):
        if self.write_service:
            self.logging("Shutting down DB Write Service.")
            self.write_service.quit()

    def _setup_database(self):
        try:
            db = DatabaseManager("chineseDict.db")
            db.connect()
            db.create_tables_if_not_exist()
            db.create_anki_integration_record()
            db.disconnect()
            self.logging("Database Tables and Indexes Set Up Successfully.")
        except Exception as e:
            self.logging(f"ERROR: Creating Tables in Database: {e}", "ERROR")
