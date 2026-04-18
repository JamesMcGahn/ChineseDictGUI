from dataclasses import dataclass, field
from typing import Any

from base.enums import JOBSTATUS


# Event
@dataclass(frozen=True)
class JobRef:
    id: str
    task: Any
    status: JOBSTATUS
    error: str | None = None
