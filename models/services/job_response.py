from dataclasses import dataclass
from typing import Generic, TypeVar

from .job_ref import JobRef

P = TypeVar("P")


# Command
@dataclass(frozen=True)
class JobResponse(Generic[P]):
    job_ref: JobRef
    payload: P | None = None
