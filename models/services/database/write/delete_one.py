from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class DeleteOnePayload(Generic[T]):
    id: int


@dataclass(frozen=True)
class DeleteOneResponse(Generic[T]):
    id: int
    count: int
    data: T
