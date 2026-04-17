from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class UpdateOnePayload(Generic[T]):
    data: T
    id: int


@dataclass(frozen=True)
class UpdateOneResponse(Generic[T]):
    data: T
    count: int
