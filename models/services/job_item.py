from dataclasses import dataclass
from typing import Generic, TypeVar

from base.enums import LESSONTASK

P = TypeVar("P")


# Command
@dataclass(frozen=True)
class JobItem(Generic[P]):
    id: str
    task: LESSONTASK
    payload: P
