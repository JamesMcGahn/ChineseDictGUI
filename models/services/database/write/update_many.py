from dataclasses import dataclass, field
from typing import Generic, TypeVar

from .update_one import UpdateOnePayload, UpdateOneResponse

T = TypeVar("T")


@dataclass(frozen=True)
class UpdateManyPayload(Generic[T]):
    data: list[UpdateOnePayload[T]] = field(default_factory=list)


@dataclass(frozen=True)
class UpdateManyResponse(Generic[T]):
    count: int
    data: list[UpdateOneResponse[T]] = field(default_factory=list)
