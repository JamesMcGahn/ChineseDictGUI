import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from functools import partial

from PySide6.QtCore import QThread, Signal

from db import DatabaseManager
from db.dals import AnkiIntegrationDAL, SentsDAL, WordsDAL
from db.workers import AnkiIntQueryWorker, SentsQueryWorker, WordsQueryWorker
from models.dictionary import Sentence, Word
from services.network import NetworkWorker, SessionManager

from .anki_find_id_inlocal_worker import FindAnkiIDsInLocalWorker
from .anki_get_ids_worker import AnkiGetNoteIDsWorker
from .anki_get_note_info_worker import AnkiGetNoteInfoWorker


class AnkiSyncImportThread(QThread):
    finished = Signal()
    update_add_sync_completed = Signal()

    def __init__(self, words_deckName, sents_deckName):
        super().__init__()
        self.words_deckName = words_deckName
        self.sents_deckName = sents_deckName
        self.deck_types_list = deque(["words", "sents"])
        self.deck_type = "sents"
        self.executor = ThreadPoolExecutor(max_workers=6)
        self.cards_to_sync = []
        self.db = DatabaseManager("chineseDict.db")
        self.sentsDAL = SentsDAL(self.db)
        self.wordsDAL = WordsDAL(self.db)
        self.sync_in_progress = False
        self.sync_tasks_remaining = 0

        self.update_add_sync_completed.connect(self.get_all_anki_deck_ids)

    def run(self):
        if self.sync_in_progress:
            return
        print(
            f"Starting Anki Import Sync in thread: {threading.get_ident()} - {QThread.currentThread()}  - {self.thread()}"
        )
        # step 1 connect to database
        print("# step 1 connect to database")
        self.db.connect()
        adb = AnkiIntegrationDAL(self.db)
        # step 2 query integration information -
        che = adb.get_anki_integration()
        (id, anki_import_time, local_import_time, initialSyncDone) = che.fetchone()
        # print(id, anki_import_time, local_import_time, initialSyncDone)
        self.local_import_time = local_import_time

        # step 3 check if initial baseline sync was completed
        print("# step 3 checking if initial baseline sync was completed")
        if initialSyncDone == 0:
            print("Initial baseline sync was not completed. Ending sync.")
            self.finished.emit()
            self.quit()
            return

        else:
            print("# intial sync was completed. Starting Sync.")
            self.sync_next_deck()

    def sync_next_deck(self):
        if self.sync_in_progress:
            return

        if self.deck_types_list:
            self.sync_in_progress = True
            self.cards_to_sync = []
            self.deck_type = self.deck_types_list.popleft()
            print(
                f"Starting Sync Process for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
            )
            self.get_edited_cards()

        else:
            print("**** Sync Complete - Card updates and adding complete")

    # step 5 query edited/new records from local db for this time interval
    def get_edited_cards(self):
        print(
            f"Getting Edited Cards for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
        )


# step 1 connect to database
# step 2 query integration information -
# step 3 check if initial baseline sync was completed
# step 4 figure out the time difference between last sync
# step 5 query edited/new records from local db for this time interval
# - WHERE anki_id IS NULL OR local_update > anki_update
# step 6 check if record local_update is > integration table local_update
# step 7 export notes to anki
# - Use addNotes for new
# - Use updateNoteFields for updates
# step 8: Update local DB records
# - Set anki_id (if new)
# - Set anki_update = now()
# step 9: Update integration table with current timestamp
# step 10: Signal sync complete
