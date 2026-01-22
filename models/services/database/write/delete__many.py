from dataclasses import dataclass, field
from typing import Generic, TypeVar

from .delete_one import DeleteOnePayload, DeleteOneResponse

T = TypeVar("T")


@dataclass(frozen=True)
class DeleteManyPayload(Generic[T]):
    data: list[DeleteOnePayload] = field(default_factory=list)


@dataclass(frozen=True)
class DeleteManyResponse(Generic[T]):
    ids: list[int] = field(default_factory=list)
    count: int
    data: list[DeleteOneResponse[T]] = field(default_factory=list)
