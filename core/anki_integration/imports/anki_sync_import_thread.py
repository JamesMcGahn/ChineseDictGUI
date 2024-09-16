import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime

from PySide6.QtCore import QThread, Signal

from db import DatabaseManager
from db.dals import AnkiIntegrationDAL
from db.workers import AnkiIntQueryWorker, SentsQueryWorker, WordsQueryWorker
from models.dictionary import Sentence, Word

from .anki_find_id_inlocal_worker import FindAnkiIDsInLocalWorker
from .anki_get_ids_worker import AnkiGetNoteIDsWorker
from .anki_get_note_info_worker import AnkiGetNoteInfoWorker


class AnkiSyncImportThread(QThread):
    finished = Signal()

    def run(self):
        # step 1 connect to database
        db = DatabaseManager("chineseDict.db")
        db.connect()
        adb = AnkiIntegrationDAL(db)
        # step 2 query integration information -
        che = adb.get_anki_integration()
        (id, anki_import_time, local_import_time, initialSyncDone) = che.fetchone()
        print(id, anki_import_time, local_import_time, initialSyncDone)

        # step 3 check if initial baseline sync was completed

        # step 4 figure out the time difference between last sync and current time in days

        last_sync_date = datetime.fromtimestamp(anki_import_time).date()
        today = date.today()
        delta_days = (today - last_sync_date).days
        print(delta_days)
        print(max(delta_days, 1))

        # step 5 query edited notes ids from anki for this time interval
        # step 6 get notes info for these ids
        # step 7 filter notes > precise time db last sync integration time
        # step 8 check for notes already in the database
        # step 9 insert new words and sentences
        # step 10 update words and sentences already in the database
        # step 11 get all ids from anki database
        # step 12 get all anki IDs from local database
        # step 13 compare and delete anki IDs from localthat arent in anki anymore
        # step 14 update integration table with the current time
