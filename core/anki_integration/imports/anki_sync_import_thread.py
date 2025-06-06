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
        self.anki_import_time = anki_import_time

        # step 3 check if initial baseline sync was completed
        print("# step 3 checking if initial baseline sync was completed")
        if initialSyncDone == 0:
            print("Initial baseline sync was not completed. Ending sync.")
            self.finished.emit()
            self.quit()
            return
        # step 4 figure out the time difference between last sync and current time in days
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
        # step 6 get notes info for these ids

    def get_edited_cards(self):
        print(
            f"Getting Edited Cards for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
        )
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
        self.networker_worker_thread = QThread()
        self.networker_w = NetworkWorker(
            self.session, "GET", "http://127.0.0.1:8765", json=json, timeout=20
        )
        self.networker_worker_thread.start()
        self.networker_w.moveToThread(self.networker_worker_thread)
        self.networker_w.finished.connect(self.networker_w.deleteLater)
        self.networker_w.response_sig.connect(self.received_edited_cards)
        self.networker_worker_thread.finished.connect(
            self.networker_worker_thread.deleteLater
        )
        self.networker_w.start_work.emit()

    def received_edited_cards(self, status, response):
        print(
            f"Received Edited Cards for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
        )
        # print("R", status, response)
        if status == "success" and response:
            note_ids_response = response.json()
            note_ids = note_ids_response["result"]
            # print("note_ids", note_ids)
            if note_ids:
                print(
                    f"Getting Detailed Note information for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
                )
                self.get_noteinfo_worker = AnkiGetNoteInfoWorker(note_ids)
                self.worker_thread = QThread()
                self.get_noteinfo_worker.moveToThread(self.worker_thread)
                self.worker_thread.start()
                self.get_noteinfo_worker.response_sig.connect(self.notes_response)
                self.get_noteinfo_worker.finished.connect(
                    self.get_noteinfo_worker.deleteLater
                )
                self.get_noteinfo_worker.start_work.emit()
                self.worker_thread.finished.connect(self.worker_thread.deleteLater)
                # self.executor.submit(self.get_noteinfo_worker.do_work)
            else:
                print(
                    f"There are no notes changes available for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
                )
                self.update_add_sync_completed.emit()
        else:
            print(
                f"Failed to Receive Edited Cards for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
            )

    # step 7 filter notes > precise time db last sync integration time

    def notes_response(self, status, response):
        # print(status, response)

        if status == "success" and response:
            print(
                f"Recieved Detailed Note information for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
            )
            card_info = response["result"]
            for card in card_info:
                if card["mod"] > self.anki_import_time:
                    # print(card)
                    self.cards_to_sync.append(card)

            # step 8 check for notes already in the database
            if self.cards_to_sync:
                if self.deck_type == "sents":
                    self.sents_sync()

                elif self.deck_type == "words":
                    self.words_sync()
            else:
                print(
                    f"No Cards to Sync for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
                )
                self.update_add_sync_completed.emit()
        else:
            print(
                f"Failed to Recieve Detailed Note information for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
            )

    def sents_sync(self):
        print("Starting Syncing Sentences Cards with the Database")
        self.db.connect()
        self.sentsDAL = SentsDAL(self.db)
        sents_to_add = []
        sents_to_update = []
        for sent in self.cards_to_sync:
            che = self.sentsDAL.get_sentence_by_ankiid(sent["noteId"])

            word_fields = sent["fields"]
            sentence = Sentence(
                chinese=word_fields["Chinese"]["value"],
                english=word_fields["English"]["value"],
                pinyin=word_fields["Pinyin"]["value"],
                audio=None,
                level=word_fields["Notes"]["value"],
                anki_audio=word_fields["Audio"]["value"],
                anki_id=sent["noteId"],
                anki_update=sent["mod"],
            )
            sent_in_db = che.fetchone()
            if sent_in_db:
                # print(sent_in_db)

                id, *_, local_update = sent_in_db
                if local_update is None or sentence.anki_update > local_update:
                    sentence.id = id
                    sents_to_update.append(
                        {"id": sentence.id, "updates": vars(sentence)}
                    )
                else:
                    print(f"Skipping Anki update for {sentence.id} — local is newer")
            else:
                sents_to_add.append(sentence)

        print("******************************")
        # print(sents_to_update)
        print("******************************")
        # print(sents_to_add)
        # step 9.a insert new sentences

        self.sync_tasks_remaining = 0
        if sents_to_add:
            self.sync_tasks_remaining += 1
            self.dbworker = SentsQueryWorker("insert_sentences", sentences=sents_to_add)
            self.dbworker.moveToThread(self)
            self.dbworker.error_occurred.emit(self.error_occured)
            self.dbworker.finished.connect(self.wait_for_sync_complete)
            self.dbworker.finished.connect(self.dbworker.deleteLater)
            self.dbworker.do_work()
        # step 10.a update sentences already in the database
        if sents_to_update:
            self.sync_tasks_remaining += 1
            print("updating ====================")
            self.updatedbworker = SentsQueryWorker(
                "update_sentences", sentences=sents_to_update
            )
            self.updatedbworker.moveToThread(self)
            self.updatedbworker.error_occurred.emit(self.error_occured)
            self.updatedbworker.finished.connect(self.wait_for_sync_complete)
            self.updatedbworker.finished.connect(self.updatedbworker.deleteLater)
            self.updatedbworker.do_work()

        if not sents_to_add and not sents_to_update:
            self.wait_for_sync_complete()

    def words_sync(self):

        print("Starting Syncing Word Cards with the Database")

        self.db.connect()

        words_to_add = []
        words_to_update = []
        for word in self.cards_to_sync:
            cha = self.wordsDAL.get_word_by_ankiid(word["noteId"])
            word_fields = word["fields"]
            word = Word(
                chinese=word_fields["Chinese"]["value"],
                definition=word_fields["English"]["value"],
                pinyin=word_fields["Pinyin"]["value"],
                audio=None,
                level=word_fields["Notes"]["value"],
                anki_audio=word_fields["Audio"]["value"],
                anki_id=word["noteId"],
                anki_update=word["mod"],
            )
            word_in_db = cha.fetchone()
            if word_in_db:
                # print(word_in_db)
                id, *_, local_update = word_in_db
                if local_update is None or word.anki_update > local_update:
                    word.id = id
                    words_to_update.append({"id": word.id, "updates": vars(word)})
                else:
                    print(f"Skipping Anki update for {word.id} — local is newer")
            else:
                words_to_add.append(word)

        self.sync_tasks_remaining = 0
        # step 9.b insert new words
        if words_to_add:
            self.sync_tasks_remaining += 1
            self.w_dbworker = WordsQueryWorker("insert_words", words=words_to_add)
            self.w_dbworker.moveToThread(self)
            self.w_dbworker.error_occurred.emit(self.error_occured)
            self.w_dbworker.finished.connect(self.wait_for_sync_complete)
            self.w_dbworker.finished.connect(self.w_dbworker.deleteLater)
            self.w_dbworker.do_work()
        # step 10.b update words already in the database
        if words_to_update:
            self.sync_tasks_remaining += 1
            print("updating ====================")
            self.w_updatedbworker = WordsQueryWorker(
                "update_words", words=words_to_update
            )
            self.w_updatedbworker.moveToThread(self)
            self.w_updatedbworker.error_occurred.emit(self.error_occured)
            self.w_updatedbworker.finished.connect(self.wait_for_sync_complete)
            self.w_updatedbworker.finished.connect(self.w_updatedbworker.deleteLater)
            self.w_updatedbworker.do_work()

        if not words_to_add and not words_to_update:
            self.wait_for_sync_complete()

    def wait_for_sync_complete(self):
        self.sync_tasks_remaining -= 1
        if self.sync_tasks_remaining == 0:
            self.update_add_sync_completed.emit()

    # step 11 get all ids from anki database
    def get_all_anki_deck_ids(self):
        print(
            f"Getting All Anki Ids for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
        )
        deck_name = (
            self.sents_deckName if self.deck_type == "sents" else self.words_deckName
        )
        self.anki_get_note_ids = AnkiGetNoteIDsWorker(deck_name)
        self.id_worker_thread = QThread()
        self.anki_get_note_ids.moveToThread(self.id_worker_thread)
        self.id_worker_thread.start()
        self.anki_get_note_ids.received_response.connect(self.get_all_db_anki_Ids)
        self.anki_get_note_ids.finished.connect(self.anki_get_note_ids.deleteLater)
        self.anki_get_note_ids.start_work.emit()
        self.id_worker_thread.finished.connect(self.id_worker_thread.deleteLater)

    # step 12 get all anki IDs from local database
    def get_all_db_anki_Ids(self, status, response, errorType):
        response = response.json()

        if "result" not in response:
            print("No result in the response")
            return

        print(
            f"Getting All Database Ids for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
        )
        if self.deck_type == "sents":
            sents_anki_external_ids = response["result"]
            print("Received All Sentence Anki IDS")
            self.db.connect()
            local_anki_ids = self.sentsDAL.get_sentence_all_anki_ids()
            local_anki_ids = local_anki_ids.fetchall()
            local_anki_ids = [sent[0] for sent in local_anki_ids]

            self.delete_ids_not_in_anki(local_anki_ids, sents_anki_external_ids)
        else:
            print("Received All Word Anki IDS")
            words_anki_external_ids = response["result"]
            self.db.connect()
            local_anki_ids = self.wordsDAL.get_words_all_anki_ids()
            local_anki_ids = local_anki_ids.fetchall()
            local_anki_ids = [word[0] for word in local_anki_ids]

            self.delete_ids_not_in_anki(local_anki_ids, words_anki_external_ids)

    # step 13 compare and delete anki IDs from localthat arent in anki anymore

    def delete_ids_not_in_anki(self, local_ids, anki_ids):
        anki_id_set = set(anki_ids)
        ids_to_delete = [id_ for id_ in local_ids if id_ not in anki_id_set]

        if len(ids_to_delete) == 0:
            self.update_db_integration_record()
            return

        print(
            f"Deleting Ids for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
        )
        if self.deck_type == "sents":
            self.s_del_dbworker = SentsQueryWorker(
                "delete_sentences", ids=ids_to_delete
            )
            self.s_del_dbworker.moveToThread(self)
            self.s_del_dbworker.error_occurred.emit(self.error_occured)
            self.s_del_dbworker.finished.connect(self.update_db_integration_record)
            self.s_del_dbworker.finished.connect(self.s_del_dbworker.deleteLater)
            self.s_del_dbworker.do_work()
        else:
            self.w_del_dbworker = WordsQueryWorker("delete_words", ids=ids_to_delete)
            self.w_del_dbworker.moveToThread(self)
            self.w_del_dbworker.error_occurred.emit(self.error_occured)
            self.w_del_dbworker.finished.connect(self.update_db_integration_record)
            self.w_del_dbworker.finished.connect(self.w_del_dbworker.deleteLater)
            self.w_del_dbworker.do_work()

    # step 14 update integration table with the current time

    def update_db_integration_record(self):
        timestamp = int(time.time())
        self.ankiDb = AnkiIntQueryWorker(
            "update_integration", updates={"anki_update": timestamp}
        )

        def _continue_sync():
            if self.deck_type == "sents":
                print("** Completed syncing Sentences.")
            else:
                print("** Completed syncing Words.")
            self.sync_in_progress = False

            self.sync_next_deck()

        self.ankiDb.moveToThread(self)
        self.ankiDb.error_occurred.emit(self.error_occured)
        self.ankiDb.finished.connect(self.ankiDb.deleteLater)
        self.ankiDb.finished.connect(_continue_sync)

        self.ankiDb.do_work()

    def error_occured(self, message):
        print(message)
        # TODO: do something about error - Toast?
