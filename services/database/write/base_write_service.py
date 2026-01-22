import sqlite3
from functools import wraps
from typing import Callable, Generic, ParamSpec, TypeVar

from PySide6.QtCore import Signal, Slot

from base import QObjectBase
from base.enums import DBOPERATION
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

from ..db_manager import DatabaseManager

T = TypeVar("T")
P = ParamSpec("P")


class BaseWriteService(Generic[T], QObjectBase):
    finished = Signal()
    pagination = Signal(object, int, int, int, bool, bool)
    error_occurred = Signal(str)
    result = Signal(list)
    task_complete = Signal(object, object)

    def __init__(self, job_ref: JobRef, payload: DBJobPayload):
        super().__init__()
        self.db_manager: DatabaseManager | None = None
        self.job_ref = job_ref
        self.payload = payload

        self.operation_mapping = {
            DBOPERATION.INSERT_ONE: (
                DBJobPayload[InsertOnePayload[T]],
                self.insert_one,
            ),
            DBOPERATION.INSERT_MANY: (
                DBJobPayload[InsertManyPayload[T]],
                self.insert_many,
            ),
            DBOPERATION.UPDATE_ONE: (
                DBJobPayload[UpdateOnePayload[T]],
                self.update_one,
            ),
            DBOPERATION.UPDATE_MANY: (
                DBJobPayload[UpdateManyPayload[T]],
                self.update_many,
            ),
            DBOPERATION.DELETE_ONE: (
                DBJobPayload[DeleteOnePayload[T]],
                self.delete_one,
            ),
            DBOPERATION.DELETE_MANY: (
                DBJobPayload[DeleteManyPayload[T]],
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
                self.task_complete.emit(self.job_ref, response)
            except (
                sqlite3.IntegrityError,
                sqlite3.OperationalError,
                sqlite3.DatabaseError,
            ) as e:
                msg = f"{self.__class__.__name__}: {fn.__name__} - {e}"
                response = DBResponse(
                    ok=False,
                    data=None,
                    error=msg,
                )
                self.logging(msg, "ERROR")
                self.task_complete.emit(self.job_ref, response)
            return response

        return wrapper

    @Slot()
    def do_work(self):
        entry = self.operation_mapping.get(self.payload.operation)

        if not entry:
            raise ValueError(
                f"{self.__class__.__name__} does not support "
                f"operation {self.payload.operation}"
            )

        payload_type, handler = entry
        if not isinstance(self.payload, payload_type):
            raise TypeError(
                f"{handler.__name__} expected {payload_type.__name__}, "
                f"got {type(self.payload).__name__}"
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
