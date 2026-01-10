from dataclasses import dataclass
from typing import Generic, TypeVar

from .job_ref import JobRef

P = TypeVar("P")


@dataclass(frozen=True)
class JobItem(Generic[P]):
    job: JobRef
    payload: P
