from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class InsertOnePayload(Generic[T]):
    data: T


@dataclass(frozen=True)
class InsertOneResponse(Generic[T]):
    data: T
