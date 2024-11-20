import threading
import time
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

    def __init__(self, words_deckName, sents_deckName):
        super().__init__()
        self.words_deckName = words_deckName
        self.sents_deckName = sents_deckName
        self.deck_type = "sents"
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cards_to_sync = []
        self.db = DatabaseManager("chineseDict.db")

    def run(self):
        # step 1 connect to database
        self.db.connect()
        adb = AnkiIntegrationDAL(self.db)
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
            self.get_edited_words("words")

        # step 6 get notes info for these ids

    def get_edited_words(self, deck_type):
        self.deck_type = deck_type

        last_sync_date = datetime.fromtimestamp(self.anki_import_time).date()
        today = date.today()
        delta_days = (today - last_sync_date).days
        last_edited_days = max(delta_days, 1)
        # step 5 query edited notes ids from anki for this time interval
        self.session = SessionManager()
        # TODO REMOVE hardcoded test time
        print("days", last_edited_days)
        deck_name = (
            self.sents_deckName if self.deck_type == "sents" else self.words_deckName
        )

        json = {
            "action": "findNotes",
            "version": 6,
            "params": {"query": f'deck:"{deck_name}" edited:{last_edited_days}'},
        }
        self.networker_w = NetworkWorker(
            self.session, "GET", "http://127.0.0.1:8765", json=json
        )
        self.networker_w.moveToThread(self)
        self.networker_w.response_sig.connect(self.received_edited_words)

        self.networker_w.do_work()

    def received_edited_words(self, status, response):
        print("hhhhhhhhh 1111")
        print(status, response)
        if status == "success" and response:
            note_ids_response = response.json()
            note_ids = note_ids_response["result"]
            if note_ids:
                self.get_noteinfo_worker = AnkiGetNoteInfoWorker(note_ids)
                self.get_noteinfo_worker.response_sig.connect(self.notes_response)

                self.get_noteinfo_worker.moveToThread(self.thread())
                self.executor.submit(self.get_noteinfo_worker.do_work)
            else:
                print("There are no notes changes available")

    # step 7 filter notes > precise time db last sync integration time

    def notes_response(self, status, response):
        print(status, response)
        print("hhhhhhhhh")
        if status == "success" and response:
            card_info = response["result"]
            for card in card_info:
                if card["mod"] > self.anki_import_time:
                    print(card)
                    self.cards_to_sync.append(card)

            # step 8 check for notes already in the database
            if self.cards_to_sync:
                if self.deck_type == "sents":
                    sentsDAL = SentsDAL(self.db)
                    sents_to_add = []
                    sents_to_update = []
                    for sent in self.cards_to_sync:
                        che = sentsDAL.get_sentence_by_ankiid(sent["noteId"])

                        word_fields = sent["fields"]
                        sentence = Sentence(
                            chinese=word_fields["中文"]["value"],
                            english=word_fields["English"]["value"],
                            pinyin=word_fields["Pinyin"]["value"],
                            audio=None,
                            level=word_fields["Notes"]["value"],
                            anki_audio=word_fields["audio"]["value"],
                            anki_id=sent["noteId"],
                            anki_update=sent["mod"],
                        )
                        sent_in_db = che.fetchone()
                        if sent_in_db:
                            print(sent_in_db)
                            id, *_ = sent_in_db
                            sentence.id = id
                            sents_to_update.append(
                                {"id": sentence.id, "updates": vars(sentence)}
                            )
                        else:
                            sents_to_add.append(sentence)

                    print("******************************")
                    print(sents_to_update)
                    print("******************************")
                    print(sents_to_add)
                    # step 9.a insert new sentences
                    if sents_to_add:
                        self.dbworker = SentsQueryWorker(
                            self.db,
                            "insert_sentences",
                            sentences=sents_to_add,
                        )
                        self.dbworker.moveToThread(self)
                        self.dbworker.error_occurred.emit(self.error_occured)
                        self.dbworker.finished.connect(self.dbworker.deleteLater)
                        self.dbworker.do_work()
                    # step 10.a update sentences already in the database
                    if sents_to_update:
                        print("updating ====================")
                        self.updatedbworker = SentsQueryWorker(
                            self.db,
                            "update_sentences",
                            sentences=sents_to_update,
                        )
                        self.updatedbworker.moveToThread(self)
                        self.updatedbworker.error_occurred.emit(self.error_occured)
                        self.updatedbworker.finished.connect(
                            self.updatedbworker.deleteLater
                        )
                        self.updatedbworker.do_work()

                elif self.deck_type == "words":
                    wordsDAL = WordsDAL(self.db)
                    words_to_add = []
                    words_to_update = []
                    for word in self.cards_to_sync:
                        cha = wordsDAL.get_word_by_ankiid(word["noteId"])
                        word_fields = word["fields"]
                        word = Word(
                            chinese=word_fields["中文"]["value"],
                            definition=word_fields["English"]["value"],
                            pinyin=word_fields["Pinyin"]["value"],
                            audio=None,
                            level=word_fields["Notes"]["value"],
                            anki_audio=word_fields["audio"]["value"],
                            anki_id=word["noteId"],
                            anki_update=word["mod"],
                        )
                        word_in_db = cha.fetchone()
                        if word_in_db:
                            print(word_in_db)
                            id, *_ = word_in_db
                            word.id = id
                            words_to_update.append(
                                {"id": word.id, "updates": vars(word)}
                            )
                        else:
                            words_to_add.append(word)
                    # step 9.b insert new words
                    if words_to_add:
                        self.w_dbworker = WordsQueryWorker(
                            self.db,
                            "insert_words",
                            words=words_to_add,
                        )
                        self.w_dbworker.moveToThread(self)
                        self.w_dbworker.error_occurred.emit(self.error_occured)
                        self.w_dbworker.finished.connect(self.w_dbworker.deleteLater)
                        self.w_dbworker.do_work()
                    # step 10.b update words already in the database
                    if words_to_update:
                        print("updating ====================")
                        self.w_updatedbworker = WordsQueryWorker(
                            self.db,
                            "update_words",
                            words=words_to_update,
                        )
                        self.w_updatedbworker.moveToThread(self)
                        self.w_updatedbworker.error_occurred.emit(self.error_occured)
                        self.w_updatedbworker.finished.connect(
                            self.w_updatedbworker.deleteLater
                        )
                        self.w_updatedbworker.do_work()

        # step 11 get all ids from anki database
        # step 12 get all anki IDs from local database
        # step 13 compare and delete anki IDs from localthat arent in anki anymore
        # step 14 update integration table with the current time

    def error_occured(self, message):
        print(message)
        # TODO: do something about error - Toast?
