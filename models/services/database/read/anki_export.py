from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class AnkiExport(Generic[T]):
    data: list[T] = field(default_factory=list)
