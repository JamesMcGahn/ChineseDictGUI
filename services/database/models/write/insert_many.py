from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class InsertManyPayload(Generic[T]):
    data: list[T] = field(default_factory=list)


@dataclass(frozen=True)
class InsertManyResponse(Generic[T]):
    data: list[T] = field(default_factory=list)
