from dataclasses import dataclass
from typing import Any, Generic, TypeVar

P = TypeVar("P")


# Command
@dataclass(frozen=True)
class JobRequest(Generic[P]):
    id: str
    task: Any
    payload: P
