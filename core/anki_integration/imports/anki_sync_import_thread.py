import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime

from PySide6.QtCore import QThread, Signal

from db import DatabaseManager
from db.dals import AnkiIntegrationDAL
from db.workers import AnkiIntQueryWorker, SentsQueryWorker, WordsQueryWorker
from models.dictionary import Sentence, Word
from services.network import NetworkWorker, SessionManager

from .anki_find_id_inlocal_worker import FindAnkiIDsInLocalWorker
from .anki_get_ids_worker import AnkiGetNoteIDsWorker
from .anki_get_note_info_worker import AnkiGetNoteInfoWorker


class AnkiSyncImportThread(QThread):
    finished = Signal()

    def __init__(self, words_deckName, sents_deckName):
        super().__init__()
        self.words_deckName = words_deckName
        self.sents_deckName = sents_deckName
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cards_to_sync = []

    def run(self):
        # step 1 connect to database
        db = DatabaseManager("chineseDict.db")
        db.connect()
        adb = AnkiIntegrationDAL(db)
        # step 2 query integration information -
        che = adb.get_anki_integration()
        (id, anki_import_time, local_import_time, initialSyncDone) = che.fetchone()
        print(id, anki_import_time, local_import_time, initialSyncDone)
        self.anki_import_time = anki_import_time

        # step 3 check if initial baseline sync was completed

        if initialSyncDone == 0:
            self.finished.emit()
            self.quit()

        # step 4 figure out the time difference between last sync and current time in days
        else:
            last_sync_date = datetime.fromtimestamp(self.anki_import_time).date()
            today = date.today()
            delta_days = (today - last_sync_date).days
            last_edited_days = max(delta_days, 1)
            # step 5 query edited notes ids from anki for this time interval
            self.session = SessionManager()
            # TODO REMOVE hardcoded test time
            print("days", last_edited_days)
            json = {
                "action": "findNotes",
                "version": 6,
                "params": {
                    "query": f'deck:"{self.sents_deckName}" edited:{last_edited_days}'
                },
            }
            self.networker_w = NetworkWorker(
                self.session, "GET", "http://127.0.0.1:8765", json=json
            )
            self.networker_w.moveToThread(self)
            self.networker_w.response_sig.connect(
                lambda status, res: self.received_edited_words(
                    status, res, self.sents_deckName
                )
            )

            self.networker_w.do_work()

        # step 6 get notes info for these ids

    def received_edited_words(self, status, response):
        print(status, response)
        if status == "success" and response:
            note_ids_response = response.json()
            note_ids = note_ids_response["result"]
            if note_ids:
                self.get_noteinfo_worker = AnkiGetNoteInfoWorker(note_ids)
                self.get_noteinfo_worker.response_sig.connect(self.notes_response)
                # self.get_noteinfo_worker.moveToThread(s)
                self.executor.submit(self.get_noteinfo_worker.do_work)
            else:
                print("There are no notes changes available")

    def notes_response(self, status, response):
        print(status, response)

        if status == "success" and response:
            card_info = response["result"]
            for card in card_info:
                if card["mod"] > self.anki_import_time:
                    print(card)
                    self.cards_to_sync.append(card)

        # step 7 filter notes > precise time db last sync integration time
        # step 8 check for notes already in the database
        # step 9 insert new words and sentences
        # step 10 update words and sentences already in the database
        # step 11 get all ids from anki database
        # step 12 get all anki IDs from local database
        # step 13 compare and delete anki IDs from localthat arent in anki anymore
        # step 14 update integration table with the current time
