from dataclasses import dataclass, field

from base.enums import JOBSTATUS, LESSONTASK

ALLOWED_PROVIDERS = {"cpod"}


# Event
@dataclass(frozen=True)
class JobRef:
    id: str
    task: LESSONTASK
    status: JOBSTATUS
