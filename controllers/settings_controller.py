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
from base.enums import JOBSTATUS, UIEVENTTYPE
from base.events import UIEvent
from models.services import JobRequest
from services.settings.enums import FIELDSTATESTATUS
from services.settings.events import FieldStateEvent, SettingUpdatedEvent
from services.settings.models import SettingUpdatedPayload, SettingValidatedPayload
from services.validation.enums import VALIDATEJOBTYPE
from services.validation.models import (
    SettingsValidatePayload,
    ValidationRequest,
    ValidationResponse,
)


class SettingsController(QObjectBase):
    verify_response_update = Signal(object)
    setting_updated = Signal(object)

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
        self.settings_service.update_setting(
            SettingUpdatedPayload(category=tab, field=key, value=value)
        )

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
        category = payload.category
        field = payload.field
        value = payload.value
        status = payload.status
        message = payload.message

        if status == FIELDSTATESTATUS.VALID:
            is_valid = True
        else:
            is_valid = False

        settings_validate_payload = SettingValidatedPayload(
            category=category, field=field, is_valid=is_valid
        )

        ui_event = UIEvent(
            event_type=UIEVENTTYPE.UPDATE,
            payload=FieldStateEvent(
                category=category, field=field, status=status, message=message
            ),
        )

        if job_res.job_ref.status == JOBSTATUS.COMPLETE:
            self._active_jobs.pop(job_id)
            self.settings_service.set_validated(settings_validate_payload)
            self.setting_updated.emit(
                SettingUpdatedEvent(category=category, field=field, value=value)
            )
            self.verify_response_update.emit(ui_event)
        elif job_res.job_ref.status in (JOBSTATUS.ERROR, JOBSTATUS.PARTIAL_ERROR):
            self._active_jobs.pop(job_id)
            self.settings_service.set_validated(settings_validate_payload)
            self.verify_response_update.emit(ui_event)
