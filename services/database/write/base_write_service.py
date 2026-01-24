import sqlite3
<<<<<<< HEAD
=======
from dataclasses import replace
>>>>>>> a595264 (change job status in decorator, implement db service in lesson workflow)
from functools import wraps
from typing import Callable, Generic, ParamSpec, TypeVar

from PySide6.QtCore import Signal, Slot

from base import QObjectBase
<<<<<<< HEAD
from base.enums import DBOPERATION
=======
from base.enums import DBOPERATION, JOBSTATUS
>>>>>>> a595264 (change job status in decorator, implement db service in lesson workflow)
from models.services import JobRef
from models.services.database import DBJobPayload, DBResponse
from models.services.database.write import (
    DeleteManyPayload,
    DeleteManyResponse,
    DeleteOnePayload,
    DeleteOneResponse,
    InsertManyPayload,
    InsertManyResponse,
    InsertOnePayload,
    InsertOneResponse,
    UpdateManyPayload,
    UpdateManyResponse,
    UpdateOnePayload,
    UpdateOneResponse,
)

from ..dals.base_DAL import BaseDAL
from ..db_manager import DatabaseManager

T = TypeVar("T")
P = ParamSpec("P")


class BaseWriteService(Generic[T], QObjectBase):
    finished = Signal()
    task_complete = Signal(object, object)

    def __init__(self, job_ref: JobRef, payload: DBJobPayload, dal: BaseDAL):
        super().__init__()
        self.db_manager: DatabaseManager | None = None
        self.job_ref = job_ref
        self.payload = payload
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
    ) -> Callable[[Callable[P, T]], Callable[P, "DBResponse[T]"]]:
        @wraps(fn)
        def wrapper(self, *args: P.args, **kwargs: P.kwargs):
            try:
                response = fn(self, *args, **kwargs)
<<<<<<< HEAD
                self.task_complete.emit(self.job_ref, response)
=======
                jobref = replace(self.job_ref, status=JOBSTATUS.COMPLETE)
                self.task_complete.emit(jobref, response)
>>>>>>> a595264 (change job status in decorator, implement db service in lesson workflow)
            except (
                sqlite3.Error,
                sqlite3.IntegrityError,
                sqlite3.OperationalError,
                sqlite3.DatabaseError,
                Exception,
            ) as e:
                msg = f"{self.__class__.__name__}: {fn.__name__} - {type(e).__name__} - {e}"
                response = DBResponse(
                    ok=False,
                    data=None,
                    error=msg,
                )
                self.logging(msg, "ERROR")
<<<<<<< HEAD
                self.task_complete.emit(self.job_ref, response)
=======
                jobref = replace(self.job_ref, status=JOBSTATUS.ERROR)
                self.task_complete.emit(jobref, response)
>>>>>>> a595264 (change job status in decorator, implement db service in lesson workflow)
            self.finished.emit()
            return response

        return wrapper

    @Slot()
    def do_work(self):
        self.log_thread()
        if self.db_manager is None:
            raise RuntimeError("DB Manager is not set")
        self.setup_dal(self._dal_class)
        entry = self.operation_mapping.get(self.payload.operation)

        if not entry:
            self.logging(
                f"{self.__class__.__name__} does not support operation {self.payload.operation}",
                "ERROR",
            )
            raise ValueError(
                f"{self.__class__.__name__} does not support operation {self.payload.operation}"
            )

        payload_type, handler = entry
        if not isinstance(self.payload.data, payload_type):
            self.logging(
                f"{handler.__name__} expected {payload_type.__name__} got {type(self.payload).__name__}",
                "ERROR",
            )
            raise TypeError(
                f"{handler.__name__} expected {payload_type.__name__} got {type(self.payload).__name__}"
            )

        handler(self.payload)

    def setup_db(self, database_manager: DatabaseManager) -> None:
        self.db_manager = database_manager

    def setup_dal(self, dal) -> None:
        self.dal = dal(self.db_manager)

    def insert_one(
        self, payload: DBJobPayload[InsertOnePayload[T]]
    ) -> DBResponse[InsertOneResponse[T]]:
        self.logging(
            f"insert_one has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"insert_one has not need implemented by {self.__class__.__name__}"
        )

    def insert_many(
        self, payload: DBJobPayload[InsertManyPayload[T]]
    ) -> DBResponse[InsertManyResponse[T]]:
        self.logging(
            f"insert_many has not been implemented by {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"insert_many has not need implemented by {self.__class__.__name__}"
        )

    def update_one(
        self, payload: DBJobPayload[UpdateOnePayload[T]]
    ) -> DBResponse[UpdateOneResponse[T]]:
        self.logging(
            f"update_one has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"update_one has not need implemented by {self.__class__.__name__}"
        )

    def update_many(
        self, payload: DBJobPayload[UpdateManyPayload[T]]
    ) -> DBResponse[UpdateManyResponse[UpdateOneResponse[T]]]:
        self.logging(
            f"update_many has not been implemented by {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"update_many has not need implemented by {self.__class__.__name__}"
        )

    def delete_one(
        self, payload: DBJobPayload[DeleteOnePayload[T]]
    ) -> DBResponse[DeleteOneResponse[T]]:
        self.logging(
            f"delete_one has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"delete_one has not need implemented by {self.__class__.__name__}"
        )

    def delete_many(
        self, payload: DBJobPayload[DeleteManyPayload[T]]
    ) -> DBResponse[DeleteManyResponse[DeleteOneResponse[T]]]:
        self.logging(
            f"delete_many has not been implemented by {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"delete_many has not need implemented by {self.__class__.__name__}"
        )
