from dataclasses import dataclass
from typing import Generic, TypeVar

from base.enums import UIEVENTTYPE

P = TypeVar("P")


@dataclass
class UIEvent(Generic[P]):
    event_type: UIEVENTTYPE
    payload: P
