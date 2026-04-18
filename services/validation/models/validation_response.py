from dataclasses import dataclass
from typing import Generic, TypeVar

from ..enums import VALIDATEJOBTYPE

T = TypeVar("T")


@dataclass(frozen=True)
class ValidationResponse(Generic[T]):
    kind: VALIDATEJOBTYPE
    data: T
