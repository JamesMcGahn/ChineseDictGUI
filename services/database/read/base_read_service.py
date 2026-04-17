import sqlite3
from functools import wraps
from typing import Callable, Generic, ParamSpec, TypeVar

from base import QObjectBase

from ..db_manager import DatabaseManager
from ..models.read import PaginationResponse

T = TypeVar("T")
P = ParamSpec("P")


class BaseReadService(Generic[T], QObjectBase):

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    @staticmethod
    def catch_sql_error(
        fn: Callable[P, T],
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        @wraps(fn)
        def wrapper(self, *args: P.args, **kwargs: P.kwargs):
            try:
                response = fn(self, *args, **kwargs)
            except (
                sqlite3.Error,
                sqlite3.IntegrityError,
                sqlite3.OperationalError,
                sqlite3.DatabaseError,
                Exception,
            ) as e:
                msg = f"{self.__class__.__name__}: {fn.__name__} - {type(e).__name__} - {e}"
                response = None
                self.logging(msg, "ERROR")
            return response

        return wrapper

    def get_by_id(self, id: int) -> T:
        self.logging(
            f"exists has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"insert_one has not need implemented by {self.__class__.__name__}"
        )

    def exists(self, items: list[T]) -> T:
        self.logging(
            f"exists has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"insert_one has not need implemented by {self.__class__.__name__}"
        )

    def anki_export(self) -> T:
        self.logging(
            f"get_anki_export has not been implemented {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"get_anki_export has not need implemented {self.__class__.__name__}"
        )

    def paginate(self, page: int, limit: int = 25) -> PaginationResponse[T]:
        self.logging(
            f"paginate has not been implemented {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"paginate has not need implemented {self.__class__.__name__}"
        )
