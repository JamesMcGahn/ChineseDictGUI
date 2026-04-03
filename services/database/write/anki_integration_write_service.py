from typing import Any

from models.dictionary import AnkiIntegration
from models.services import JobRequest
from models.services.database import DBJobPayload

from ..dals import AnkiIntegrationDAL
from .base_write_service import BaseWriteService


class AnkiIntegrationWriteService(BaseWriteService[AnkiIntegration]):

    def __init__(self, job: JobRequest[DBJobPayload[Any]]):
        super().__init__(job=job, dal=AnkiIntegrationDAL)

    @BaseWriteService.emit_db_response
    def update_one(self, payload):
        update = payload.data.data
        id = payload.data.id
        count, integration = self.dal.update_one(id, update)
        integration = None

        if integration:
            integration = AnkiIntegration(
                id=integration[0],
                anki_update=integration[0],
                local_update=integration[1],
                initial_import_done=integration[2],
            )
        return integration
