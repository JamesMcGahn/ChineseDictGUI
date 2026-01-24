from enum import StrEnum


class DBOPERATION(StrEnum):
    INSERT_ONE = "insert_one"
    INSERT_MANY = "insert_many"
    DELETE_ONE = "delete_one"
    DELETE_MANY = "delete_many"
    UPDATE_ONE = "update_one"
    UPDATE_MANY = "update_many"
