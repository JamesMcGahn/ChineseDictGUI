from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class BatchJobResponse(Generic[T]):
    success_count: int = 0
    error_count: int = 0
    total_count: int = 0
    data: T | None = None
    failed_items: list[T] | None = None

    @property
    def is_success(self):
        return self.error_count == 0

    @property
    def is_partial(self):
        return 0 < self.error_count < self.total_count

    @property
    def is_failure(self):
        return self.error_count == self.total_count

    @property
    def failure_rate(self):
        if self.total_count == 0:
            return 0
        return self.error_count / self.total_count
