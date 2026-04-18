from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from models.services import JobResponse, JobRequest
    from .models import ValidationRequest, SettingsValidatePayload
    from .enums import VALIDATEJOBTYPE
    from .base_validator import BaseValidator
    from settings.models import SettingsFieldMeta
    from .settings_meta_provider import SettingsMetaProvider

from PySide6.QtCore import Signal

from base import QObjectBase
from base.enums import JOBSTATUS
from models.services import JobRef

from .models import SettingsValidateResponse, ValidationResponse


class SettingsValidationService(QObjectBase):
    task_complete = Signal(object)

    def __init__(self, settings_meta_provider: SettingsMetaProvider):
        super().__init__()
        self.settings_meta_provider = settings_meta_provider
        self._pending_jobs = {}

    def validate(
        self, job: JobRequest[ValidationRequest[SettingsValidatePayload]]
    ) -> JobResponse[ValidationResponse]:
        self._pending_jobs[job.id] = job

        payload = job.payload.data

        field_meta: SettingsFieldMeta = self.settings_meta_provider.get_field_meta(
            payload.category, payload.field
        )

        if not field_meta:
            # Send fail task
            return

        result = field_meta.verify(payload)
        if result is None:
            return  # Send fail task
        # validator.validate(job)

        if isinstance(result, SettingsValidateResponse):
            pass
            # return self._wrap_response(job, result)

        # async jobs -> #TODO -> build dc
        # elif isinstance(result, ValidationJob):
        # self._dispatch(job, payload, result)
        # send pending status ? return self._build_pending_response(payload)

        else:
            raise ValueError("Invalid validator return type")

    def send_validation_response(self, job_id, res: SettingsValidateResponse):
        job = self._pending_jobs.get(job_id)
        if not job:
            return
        job_response = JobResponse(
            job_ref=JobRef(job_id, task=None, status=JOBSTATUS.COMPLETE),
            payload=res,
        )
        self.task_complete.emit(job_response)
