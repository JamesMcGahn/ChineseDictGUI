from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class DBResponse(Generic[T]):
    ok: bool
    data: T | None = None
    error: Exception | str | None = None
