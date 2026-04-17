from functools import wraps
from typing import Any, Callable, Generic, ParamSpec, TypeVar

from PySide6.QtCore import Signal, Slot

from base import QWorkerBase
from base.enums import JOBSTATUS
from models.services import JobRef, JobRequest, JobResponse

from ..dals.base_DAL import BaseDAL
from ..db_manager import DatabaseManager
from ..enums import DBOPERATION
from ..models import DBJobPayload
from ..models.write import (
    DeleteManyPayload,
    DeleteOnePayload,
    InsertManyPayload,
    InsertOnePayload,
    UpdateManyPayload,
    UpdateOnePayload,
    UpsertOnePayload,
)

T = TypeVar("T")
P = ParamSpec("P")


class BaseWriteService(Generic[T], QWorkerBase):
    task_complete = Signal(object)

    def __init__(self, job: JobRequest[DBJobPayload[Any]], dal: BaseDAL):
        super().__init__()
        self.db_manager: DatabaseManager | None = None
        self.job = job

        self._dal_class = dal
        self.dal: BaseDAL | None = None
        self.operation_mapping = {
            DBOPERATION.INSERT_ONE: (
                InsertOnePayload,
                self.insert_one,
            ),
            DBOPERATION.INSERT_MANY: (
                InsertManyPayload,
                self.insert_many,
            ),
            DBOPERATION.UPSERT_ONE: (
                UpsertOnePayload,
                self.upsert_one,
            ),
            DBOPERATION.UPDATE_ONE: (
                UpdateOnePayload,
                self.update_one,
            ),
            DBOPERATION.UPDATE_MANY: (
                UpdateManyPayload,
                self.update_many,
            ),
            DBOPERATION.DELETE_ONE: (
                DeleteOnePayload,
                self.delete_one,
            ),
            DBOPERATION.DELETE_MANY: (
                DeleteManyPayload,
                self.delete_many,
            ),
        }

    @staticmethod
    def emit_db_response(
        fn: Callable[P, T],
    ) -> Callable[
        [Callable[P, T]],
        Callable[P, JobResponse[T]],
    ]:
        @wraps(fn)
        def wrapper(self, *args: P.args, **kwargs: P.kwargs):
            try:
                payload = fn(self, *args, **kwargs)

                response = JobResponse(
                    job_ref=JobRef(
                        id=self.job.id,
                        task=self.job.task,
                        status=JOBSTATUS.COMPLETE,
                    ),
                    payload=payload,
                )

            except Exception as e:
                msg = f"{fn.__name__} - {type(e).__name__} - {e}"

                self.logging(msg, "ERROR")

                response = JobResponse(
                    job_ref=JobRef(
                        id=self.job.id,
                        task=self.job.task,
                        status=JOBSTATUS.ERROR,
                        error=msg,
                    ),
                    payload=None,
                )

            self.task_complete.emit(response)
            self.done.emit()
            return response

        return wrapper

    @Slot()
    def do_work(self):
        self.log_thread()
        if self.db_manager is None:
            raise RuntimeError("DB Manager is not set")
        self.setup_dal(self._dal_class)
        entry = self.operation_mapping.get(self.job.payload.operation)

        if not entry:
            self.logging(
                f"{self.__class__.__name__} does not support operation {self.job.payload.operation}",
                "ERROR",
            )
            raise ValueError(
                f"{self.__class__.__name__} does not support operation {self.job.payload.operation}"
            )

        payload_type, handler = entry
        if not isinstance(self.job.payload.data, payload_type):
            self.logging(
                f"{handler.__name__} expected {payload_type.__name__} got {type(self.job.payload).__name__}",
                "ERROR",
            )
            raise TypeError(
                f"{handler.__name__} expected {payload_type.__name__} got {type(self.job.payload).__name__}"
            )

        handler(self.job.payload)

    def setup_db(self, database_manager: DatabaseManager) -> None:
        self.db_manager = database_manager

    def setup_dal(self, dal) -> None:
        self.dal = dal(self.db_manager)

    def insert_one(self, payload: DBJobPayload[InsertOnePayload[T]]) -> T:
        self.logging(
            f"insert_one has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"insert_one has not need implemented by {self.__class__.__name__}"
        )

    def upsert_one(self, payload: DBJobPayload[UpsertOnePayload[T]]) -> T:
        self.logging(
            f"insert_one has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"insert_one has not need implemented by {self.__class__.__name__}"
        )

    def insert_many(self, payload: DBJobPayload[InsertManyPayload[T]]) -> list[T]:
        self.logging(
            f"insert_many has not been implemented by {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"insert_many has not need implemented by {self.__class__.__name__}"
        )

    def update_one(self, payload: DBJobPayload[UpdateOnePayload[T]]) -> T:
        self.logging(
            f"update_one has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"update_one has not need implemented by {self.__class__.__name__}"
        )

    def update_many(self, payload: DBJobPayload[UpdateManyPayload[T]]) -> list[T]:
        self.logging(
            f"update_many has not been implemented by {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"update_many has not need implemented by {self.__class__.__name__}"
        )

    def delete_one(self, payload: DBJobPayload[DeleteOnePayload[T]]) -> T:
        self.logging(
            f"delete_one has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"delete_one has not need implemented by {self.__class__.__name__}"
        )

    def delete_many(self, payload: DBJobPayload[DeleteManyPayload[T]]) -> list[T]:
        self.logging(
            f"delete_many has not been implemented by {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"delete_many has not need implemented by {self.__class__.__name__}"
        )
