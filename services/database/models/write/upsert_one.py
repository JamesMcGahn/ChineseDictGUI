from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class UpsertOnePayload(Generic[T]):
    data: T


@dataclass(frozen=True)
class UpsertOneResponse(Generic[T]):
    data: T
