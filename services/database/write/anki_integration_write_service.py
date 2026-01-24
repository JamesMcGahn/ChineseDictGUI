from models.dictionary import AnkiIntegration
from models.services import JobRef
from models.services.database import DBJobPayload, DBResponse
from models.services.database.write import (
    UpdateOneResponse,
)

from ..dals import AnkiIntegrationDAL
from .base_write_service import BaseWriteService


class AnkiIntegrationWriteService(BaseWriteService[AnkiIntegration]):

    def __init__(self, job_ref: JobRef, payload: DBJobPayload):
        super().__init__(job_ref, payload, dal=AnkiIntegrationDAL)

    @BaseWriteService.emit_db_response
    def update_one(self, payload):
        update = payload.data.data
        id = payload.data.id
        count, integration = self.dal.update_one(id, update)
        success = count > 0
        integration = None

        if integration:
            integration = AnkiIntegration(
                id=integration[0],
                anki_update=integration[0],
                local_update=integration[1],
                initial_import_done=integration[2],
            )
        return DBResponse(
            ok=success, data=UpdateOneResponse(data=integration, count=count)
        )
