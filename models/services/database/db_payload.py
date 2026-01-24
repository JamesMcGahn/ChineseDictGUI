from dataclasses import dataclass
from typing import Generic, TypeVar

from base.enums import DBJOBTYPE, DBOPERATION

T = TypeVar("T")


@dataclass(frozen=True)
class DBJobPayload(Generic[T]):
    kind: DBJOBTYPE
    operation: DBOPERATION
    data: T
