from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PaginationResponse(Generic[T]):
    data: list[T] = field(default_factory=list)
    table_count: int | None
    total_pages: int | None
    page: int | None
    has_prev_page: bool
    has_next_page: bool
