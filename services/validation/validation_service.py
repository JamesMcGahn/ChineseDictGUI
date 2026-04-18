from __future__ import annotations

from typing import TYPE_CHECKING

from base import QObjectBase

if TYPE_CHECKING:
    from models.services import JobResponse, JobRequest
    from .models import ValidationResponse, ValidationRequest
    from .base_validator import BaseValidator
    from .settings_meta_provider import SettingsMetaProvider

from .enums import VALIDATEJOBTYPE
from .settings_validator import SettingsValidationService


class ValidationService(QObjectBase):

    def __init__(self, settings_meta_provider: SettingsMetaProvider):
        super().__init__()
        self._validators: dict[VALIDATEJOBTYPE, BaseValidator] = {
            VALIDATEJOBTYPE.SETTINGS: SettingsValidationService(
                settings_meta_provider=settings_meta_provider
            )
        }

    def validate(
        self, job: JobRequest[ValidationRequest]
    ) -> JobResponse[ValidationResponse]:
        validator = self._validators.get(job.payload.kind)

        if not validator:
            msg = f"There is not a validator registered for {job.payload.kind}"
            self.logging(msg, "ERROR")
            raise ValueError(msg)
        validator.validate(job)
