from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.managers import (
        DatabaseServiceManager,
    )

from dataclasses import dataclass


@dataclass()
class ServiceContainer:
    db: "DatabaseServiceManager"
