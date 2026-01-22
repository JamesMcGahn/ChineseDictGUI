from typing import Generic, TypeVar

from base import QObjectBase
from models.services.database import DBResponse
from models.services.database.read import (
    AnkiExport,
    Exists,
    GetByID,
    PaginationResponse,
)

from ..db_manager import DatabaseManager

T = TypeVar("T")


class BaseReadService(Generic[T], QObjectBase):

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    def get_by_id(self, id: int) -> DBResponse[GetByID[T]]:
        self.logging(
            f"exists has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"insert_one has not need implemented by {self.__class__.__name__}"
        )

    def exists(self, items: list[T]) -> DBResponse[Exists[T]]:
        self.logging(
            f"exists has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"insert_one has not need implemented by {self.__class__.__name__}"
        )

    def anki_export(self) -> DBResponse[AnkiExport[T]]:
        self.logging(
            f"get_anki_export has not been implemented {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"get_anki_export has not need implemented {self.__class__.__name__}"
        )

    def paginate(self, page: int, limit: int = 25) -> DBResponse[PaginationResponse[T]]:
        self.logging(
            f"paginate has not been implemented {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"paginate has not need implemented {self.__class__.__name__}"
        )
