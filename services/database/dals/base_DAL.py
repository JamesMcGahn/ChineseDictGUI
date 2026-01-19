from typing import Generic, TypeVar

from base import QObjectBase

from ..db_manager import DatabaseManager

T = TypeVar("T")


class BaseDAL(Generic[T], QObjectBase):

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def count(self):
        self.logging(
            f"count has not been implemented {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"count has not need implemented {self.__class__.__name__}"
        )

    def exists(self, items: list[str]):
        self.logging(
            f"exists has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"insert_one has not need implemented by {self.__class__.__name__}"
        )

    def get_by_id(self, id: int):
        self.logging(
            f"get_by_id has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"get_by_id has not need implemented by {self.__class__.__name__}"
        )

    def insert_one(self, item: T):
        self.logging(
            f"insert_one has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"insert_one has not need implemented by {self.__class__.__name__}"
        )

    def update_one(self, id: int, updates: dict):
        self.logging(
            f"update_one has not been implemented {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"update_one has not need implemented {self.__class__.__name__}"
        )

    def delete_one_by_id(self, id: int):
        self.logging(
            f"delete_one has not been implemented by {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"delete_one has not need implemented {self.__class__.__name__}"
        )

    def delete_many_by_id(self, ids: list[int]):
        self.logging(
            f"delete_many_by_id has not been implemented {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"delete_many_by_id has not need implemented {self.__class__.__name__}"
        )

    def paginate(self, page: int, limit: int = 25):
        self.logging(
            f"paginate has not been implemented {self.__class__.__name__}", "ERROR"
        )
        raise NotImplementedError(
            f"paginate has not need implemented {self.__class__.__name__}"
        )

    def get_anki_export(self):
        self.logging(
            f"get_anki_export has not been implemented {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"get_anki_export has not need implemented {self.__class__.__name__}"
        )

    def get_by_anki_id(self, anki_id: int):
        self.logging(
            f"get_by_anki_id has not been implemented {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"get_by_anki_id has not need implemented {self.__class__.__name__}"
        )

    def get_anki_ids(self):
        self.logging(
            f"get_by_anki_id has not been implemented {self.__class__.__name__}",
            "ERROR",
        )
        raise NotImplementedError(
            f"get_by_anki_id has not need implemented {self.__class__.__name__}"
        )
