from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.settings import SettingsService
    from services.validation import ValidationService
    from services.settings.enums import SETTINGSCATEGORIES
    from services.settings.models import AppSettings
    from models.services import JobResponse
    from services.validation.models import ValidationResponse, SettingsValidateResponse

from uuid import uuid4

from PySide6.QtCore import Signal

from base import QObjectBase
from base.enums import JOBSTATUS
from models.services import JobRequest
from services.validation.enums import VALIDATEJOBTYPE
from services.validation.models import (
    SettingsValidatePayload,
    ValidationRequest,
    ValidationResponse,
)


class SettingsController(QObjectBase):
    verify_response_update = Signal(str, str, bool)

    def __init__(
        self,
        settings_service: SettingsService,
        validation_service: ValidationService,
    ):
        super().__init__()
        self.settings_service = settings_service
        self.validation_service = validation_service

        self._active_jobs: dict[str, str] = {}

        self.validation_service.task_complete.connect(self.on_validation_complete)

    def get_settings(self) -> AppSettings:
        self.settings_service.load_settings()
        return self.settings_service.get_settings()

    def get_settings_validation(self) -> dict[SETTINGSCATEGORIES, dict[str, bool]]:
        self.settings_service.load_settings()
        return self.settings_service.get_validations()

    def on_field_change(self, tab, key, value):
        # print("*** in Controller:", tab, key, value, type(value))
        self.settings_service.update_setting(category=tab, field=key, value=value)

    def on_field_verify(self, category: SETTINGSCATEGORIES, field: str, value):
        print("controller", category, field, value)

        job_id = str(uuid4())

        payload = SettingsValidatePayload(category=category, field=field, value=value)

        job = JobRequest(
            id=job_id,
            task=None,
            payload=ValidationRequest(kind=VALIDATEJOBTYPE.SETTINGS, data=payload),
        )

        self._active_jobs[job_id] = payload
        self.validation_service.validate(job)

    def on_validation_complete(
        self, job_res: JobResponse[ValidationResponse[SettingsValidateResponse]]
    ):
        job_id = job_res.job_ref.id
        if job_id not in self._active_jobs:
            return

        payload = job_res.payload.data

        if job_res.job_ref.status == JOBSTATUS.COMPLETE:
            self._active_jobs.pop(job_id)
            category = payload.category
            field = payload.field
            is_valid = payload.is_valid
            self.settings_service.set_validated(category, field, is_valid)
            self.verify_response_update.emit(category, field, is_valid)
        elif job_res.job_ref.status in (JOBSTATUS.ERROR, JOBSTATUS.PARTIAL_ERROR):
            self._active_jobs.pop(job_id)
            self.settings_service.set_validated(category, field, False)
            self.verify_response_update.emit(category, field, False)
