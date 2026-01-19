from PySide6.QtCore import Signal

from models.dictionary import AnkiIntegration
from models.services.database import DBResponse
from models.services.database.read import GetByID

from ..dals import AnkiIntegrationDAL
from .base_service import BaseService


class AnkiIntegrationReadService(BaseService[AnkiIntegration]):
    pagination = Signal(object, int, int, int, bool, bool)
    result = Signal(list)

    def __init__(self, db_manager):
        super().__init__(db_manager=db_manager)
        self.dal = AnkiIntegrationDAL(self.db_manager)

    def get_by_id(self, id):
        row = self.dal.get_by_id(id)
        item = None
        if row is not None:
            id, anki_import_time, local_import_time, initialSyncDone = row
            item = AnkiIntegration(
                anki_update=anki_import_time,
                local_update=local_import_time,
                initial_import_done=initialSyncDone,
                id=id,
            )
        return DBResponse(
            ok=True,
            data=GetByID(data=item),
        )
